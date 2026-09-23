"""
RDD2022 Dataset Formatting & Curation Script.
Converts Pascal VOC XML annotations to YOLO normalized annotation format.
Also supports generating a mock/synthetic raw dataset for verification and testing.
"""

import argparse
import logging
import os
import shutil
import xml.etree.ElementTree as ET
import random
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Class name mapping for RDD2022 dataset to our unified model classes
CLASS_MAP: Dict[str, int] = {
    "D40": 0,  # Pothole
    "pothole": 0,
    "D00": 1,  # Longitudinal Crack
    "longitudinal_crack": 1,
    "D10": 2,  # Transverse Crack
    "transverse_crack": 2,
    "D20": 3,  # Alligator Crack
    "alligator_crack": 3,
    "D43": 4,  # Waterlogging
    "D44": 4,
    "waterlogging": 4,
}

CLASS_NAMES: Dict[int, str] = {
    0: "Pothole",
    1: "Longitudinal Crack",
    2: "Transverse Crack",
    3: "Alligator Crack",
    4: "Waterlogging",
}


def convert_bbox(size: Tuple[int, int], box: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """
    Convert Pascal VOC bounding box (xmin, ymin, xmax, ymax) to YOLO format (x_center, y_center, w, h).
    """
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    x_center = (box[0] + box[2]) / 2.0
    y_center = (box[1] + box[3]) / 2.0
    w = box[2] - box[0]
    h = box[3] - box[1]
    
    # Normalize and round
    x_center = round(x_center * dw, 6)
    y_center = round(y_center * dh, 6)
    w = round(w * dw, 6)
    h = round(h * dh, 6)
    
    return (x_center, y_center, w, h)


def parse_xml_annotation(xml_path: str) -> Tuple[int, int, List[Tuple[int, float, float, float, float]]]:
    """
    Parse a Pascal VOC XML file and return width, height, and parsed objects with mapped class IDs.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    size = root.find("size")
    if size is None:
        raise ValueError(f"XML missing 'size' block: {xml_path}")
        
    width = int(size.find("width").text) # type: ignore
    height = int(size.find("height").text) # type: ignore
    
    parsed_objects = []
    for obj in root.findall("object"):
        name = obj.find("name").text # type: ignore
        if name not in CLASS_MAP:
            continue
            
        class_id = CLASS_MAP[name]
        bndbox = obj.find("bndbox")
        if bndbox is None:
            continue
            
        xmin = float(bndbox.find("xmin").text) # type: ignore
        ymin = float(bndbox.find("ymin").text) # type: ignore
        xmax = float(bndbox.find("xmax").text) # type: ignore
        ymax = float(bndbox.find("ymax").text) # type: ignore
        
        # Clip bounding box coordinates to image boundaries
        xmin = max(0.0, min(xmin, float(width)))
        xmax = max(0.0, min(xmax, float(width)))
        ymin = max(0.0, min(ymin, float(height)))
        ymax = max(0.0, min(ymax, float(height)))
        
        if xmax <= xmin or ymax <= ymin:
            continue
            
        parsed_objects.append((class_id, xmin, ymin, xmax, ymax))
        
    return width, height, parsed_objects


def process_dataset(
    raw_dir: str,
    output_dir: str,
    val_split: float = 0.2
) -> Tuple[int, int]:
    """
    Processes the raw dataset folder, partitions into train/val sets, and writes YOLO labels.
    """
    images_dir = os.path.join(raw_dir, "images")
    annotations_dir = os.path.join(raw_dir, "annotations")
    
    if not os.path.exists(images_dir) or not os.path.exists(annotations_dir):
        raise FileNotFoundError(f"Missing images/ or annotations/ folder in {raw_dir}")
        
    # Find all XML files
    xml_files = [f for f in os.listdir(annotations_dir) if f.endswith(".xml")]
    if not xml_files:
        raise ValueError(f"No XML annotations found in {annotations_dir}")
        
    # Create target YOLO structure
    for split in ["train", "val"]:
        os.makedirs(os.path.join(output_dir, "images", split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "labels", split), exist_ok=True)
        
    # Shuffle for split
    random.seed(42)
    random.shuffle(xml_files)
    
    split_idx = int(len(xml_files) * (1 - val_split))
    splits = {
        "train": xml_files[:split_idx],
        "val": xml_files[split_idx:]
    }
    
    processed_counts = {"train": 0, "val": 0}
    error_count = 0
    
    for split_name, files in splits.items():
        for xml_file in files:
            base_name = os.path.splitext(xml_file)[0]
            xml_path = os.path.join(annotations_dir, xml_file)
            
            # Find matching image file
            img_file = None
            for ext in [".jpg", ".jpeg", ".png"]:
                candidate = base_name + ext
                if os.path.exists(os.path.join(images_dir, candidate)):
                    img_file = candidate
                    break
                    
            if not img_file:
                logger.warning(f"No matching image found for annotation: {xml_file}")
                error_count += 1
                continue
                
            try:
                width, height, objects = parse_xml_annotation(xml_path)
                
                # Copy image file to split
                src_img = os.path.join(images_dir, img_file)
                dst_img = os.path.join(output_dir, "images", split_name, img_file)
                shutil.copy2(src_img, dst_img)
                
                # Write YOLO label file
                label_file = base_name + ".txt"
                label_path = os.path.join(output_dir, "labels", split_name, label_file)
                
                with open(label_path, "w") as f:
                    for class_id, xmin, ymin, xmax, ymax in objects:
                        x_center, y_center, w, h = convert_bbox((width, height), (xmin, ymin, xmax, ymax))
                        f.write(f"{class_id} {x_center} {y_center} {w} {h}\n")
                        
                processed_counts[split_name] += 1
            except Exception as e:
                logger.error(f"Error processing {xml_file}: {str(e)}")
                error_count += 1
                
    total_processed = sum(processed_counts.values())
    logger.info(f"Dataset formatting complete. Processed {total_processed} files (Train: {processed_counts['train']}, Val: {processed_counts['val']}) with {error_count} errors.")
    return total_processed, error_count


def generate_synthetic_raw_dataset(raw_dir: str, num_samples: int = 1050):
    """
    Generates a mock/synthetic raw dataset with 1,000+ files to validate pipeline logic.
    """
    logger.info(f"Generating synthetic raw dataset of {num_samples} samples at {raw_dir}...")
    images_dir = os.path.join(raw_dir, "images")
    annotations_dir = os.path.join(raw_dir, "annotations")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(annotations_dir, exist_ok=True)
    
    # Import cv2 dynamically here to avoid dependency issues if not installed
    import cv2
    import numpy as np
    
    classes_pool = ["D40", "D00", "D10", "D20", "D43"]
    
    for i in range(num_samples):
        base_name = f"road_sample_{i:04d}"
        img_name = base_name + ".jpg"
        xml_name = base_name + ".xml"
        
        # 1. Create a dummy road image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Random road background tone
        img[:] = (80 + random.randint(-10, 10), 80 + random.randint(-10, 10), 80 + random.randint(-10, 10))
        
        # Add lane mark
        cv2.line(img, (320, 0), (320, 480), (240, 240, 240), 3)
        
        # 2. Draw mock damage shapes and define bbox
        num_objects = random.randint(1, 3)
        bboxes = []
        for _ in range(num_objects):
            class_code = random.choice(classes_pool)
            
            # Define box coordinates
            w = random.randint(40, 120)
            h = random.randint(30, 80)
            xmin = random.randint(10, 640 - w - 10)
            ymin = random.randint(10, 480 - h - 10)
            xmax = xmin + w
            ymax = ymin + h
            
            bboxes.append((class_code, xmin, ymin, xmax, ymax))
            
            # Draw synthetic shape
            color = (30, 30, 30) if class_code == "D40" else (100, 100, 150)
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, -1)
            
        cv2.imwrite(os.path.join(images_dir, img_name), img)
        
        # 3. Create Pascal VOC XML string
        xml_content = f"""<annotation>
    <filename>{img_name}</filename>
    <size>
        <width>640</width>
        <height>480</height>
        <depth>3</depth>
    </size>
"""
        for class_code, xmin, ymin, xmax, ymax in bboxes:
            xml_content += f"""    <object>
        <name>{class_code}</name>
        <bndbox>
            <xmin>{xmin}</xmin>
            <ymin>{ymin}</ymin>
            <xmax>{xmax}</xmax>
            <ymax>{ymax}</ymax>
        </bndbox>
    </object>
"""
        xml_content += "</annotation>"
        
        with open(os.path.join(annotations_dir, xml_name), "w") as f:
            f.write(xml_content)
            
    logger.info("Synthetic raw dataset generated successfully.")


def create_dataset_config_yaml(yaml_path: str, data_dir: str):
    """
    Creates the road_damage.yaml dataset configuration file.
    """
    # Normalize paths to use forward slashes for cross-platform YOLO compatibility
    normalized_data_dir = data_dir.replace("\\", "/")
    
    yaml_content = f"""# RoadDamage Dataset Configuration for YOLOv8
path: {normalized_data_dir}
train: images/train
val: images/val

# Class names mapping
names:
  0: Pothole
  1: Longitudinal Crack
  2: Transverse Crack
  3: Alligator Crack
  4: Waterlogging
"""
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    logger.info(f"Dataset config file written to {yaml_path}")


def main():
    parser = argparse.ArgumentParser(description="RDD2022 Dataset Formatting Tool")
    parser.add_argument("--raw-dir", type=str, default="ai_engine/data/raw", help="Path to raw dataset folder")
    parser.add_argument("--output-dir", type=str, default="ai_engine/data", help="Path to write formatted YOLO dataset")
    parser.add_argument("--generate-synthetic", action="store_true", help="Generate synthetic raw dataset for pipeline verification")
    parser.add_argument("--num-samples", type=int, default=1050, help="Number of synthetic samples to generate")
    
    args = parser.parse_args()
    
    # Resolve relative paths relative to workspace root
    raw_dir_abs = os.path.abspath(args.raw_dir)
    output_dir_abs = os.path.abspath(args.output_dir)
    
    if args.generate_synthetic:
        generate_synthetic_raw_dataset(raw_dir_abs, num_samples=args.num_samples)
        
    try:
        processed, errors = process_dataset(raw_dir_abs, output_dir_abs)
        
        # Write config YAML file
        yaml_path = os.path.join(output_dir_abs, "road_damage.yaml")
        create_dataset_config_yaml(yaml_path, output_dir_abs)
        
        print(f"\n--- Processing Completed ---")
        print(f"Total processed: {processed}")
        print(f"Total errors: {errors}")
        print(f"Config file: {yaml_path}")
    except Exception as e:
        logger.error(f"Failed to process dataset: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
