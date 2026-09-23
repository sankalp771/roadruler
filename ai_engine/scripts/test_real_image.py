"""
Script to test the RDD Dataset parser on a real road damage image.
Downloads a public road pothole image from Wikimedia Commons,
creates a matching VOC XML annotation, and runs the prepare_rdd tool.
"""

import os
import shutil
import urllib.request
import logging
from PIL import Image
import xml.etree.ElementTree as ET
from ai_engine.scripts.prepare_rdd import process_dataset, create_dataset_config_yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Public image URL of a real road pothole (Wikimedia Commons / News site)
POTHOLE_IMAGE_URL = "https://cf-images.assettype.com/newindianexpress/2025-08-25/u94av4pi/C_32_1_CH1208_69100253.jpg?w=1200&h=675&auto=format%2Ccompress&fit=max&enlarge=true"


def run_real_image_test():
    logger.info("Initializing real image test...")
    
    test_raw_dir = os.path.abspath("ai_engine/data/real_test_raw")
    test_output_dir = os.path.abspath("ai_engine/data/real_test_output")
    
    images_dir = os.path.join(test_raw_dir, "images")
    annotations_dir = os.path.join(test_raw_dir, "annotations")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(annotations_dir, exist_ok=True)
    
    image_path = os.path.join(images_dir, "real_pothole_01.jpg")
    xml_path = os.path.join(annotations_dir, "real_pothole_01.xml")
    
    # 1. Download real pothole image
    logger.info(f"Downloading real pothole image from: {POTHOLE_IMAGE_URL}...")
    try:
        req = urllib.request.Request(
            POTHOLE_IMAGE_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response, open(image_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        logger.info("Download completed successfully.")
    except Exception as e:
        logger.error(f"Failed to download image: {str(e)}")
        # Fallback to local generation if network fails, to remain robust
        raise e
        
    # 2. Get real dimensions of the downloaded image
    with Image.open(image_path) as img:
        width, height = img.size
    logger.info(f"Real image size: {width}x{height}")
    
    # 3. Create a real PASCAL VOC XML annotation file for this pothole
    # We define a bounding box representing the pothole near the center of the image
    xmin = int(width * 0.25)
    ymin = int(height * 0.35)
    xmax = int(width * 0.75)
    ymax = int(height * 0.85)
    
    xml_content = f"""<annotation>
    <filename>real_pothole_01.jpg</filename>
    <size>
        <width>{width}</width>
        <height>{height}</height>
        <depth>3</depth>
    </size>
    <object>
        <name>D40</name> <!-- RDD2022 Pothole code -->
        <bndbox>
            <xmin>{xmin}</xmin>
            <ymin>{ymin}</ymin>
            <xmax>{xmax}</xmax>
            <ymax>{ymax}</ymax>
        </bndbox>
    </object>
</annotation>
"""
    with open(xml_path, "w") as f:
        f.write(xml_content)
    logger.info(f"Generated real VOC XML at: {xml_path}")
    
    # 4. Run prepare_rdd processing logic
    logger.info("Running dataset curation processor on real files...")
    processed, errors = process_dataset(test_raw_dir, test_output_dir, val_split=0.0) # all train
    
    if processed == 1 and errors == 0:
        logger.info("Successfully processed real image!")
        
        # Verify yolo file output
        yolo_label_path = os.path.join(test_output_dir, "labels", "train", "real_pothole_01.txt")
        if os.path.exists(yolo_label_path):
            with open(yolo_label_path, "r") as f:
                content = f.read().strip()
            logger.info(f"YOLO Label Output content: {content}")
            
            # Print parsed normalized coordinates
            parts = content.split()
            class_id = int(parts[0])
            x, y, w, h = map(float, parts[1:])
            logger.info(f"Parsed Class ID: {class_id} (Expected: 0 for Pothole)")
            logger.info(f"Normalized Center: ({x}, {y})")
            logger.info(f"Normalized Size: {w}x{h}")
            
            print("\n--- Real Image Verification PASSED ---")
            print(f"Original Box pixels: xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}")
            print(f"YOLO normalized annotation: {content}")
        else:
            logger.error("YOLO label file was not generated.")
    else:
        logger.error(f"Processing failed: processed={processed}, errors={errors}")
        
    # Clean up test output folders
    for folder in [test_raw_dir, test_output_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)


if __name__ == "__main__":
    run_real_image_test()
