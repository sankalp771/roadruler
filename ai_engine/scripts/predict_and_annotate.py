"""
Script to predict potholes in a user-provided image set,
draw bounding boxes (boxing), and save the annotated results.
Also copies them to the artifact folder so they can be viewed in the UI.
"""

import os
import shutil
import cv2
import logging
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

INPUT_DIR = "ai_engine/pothole_imageset"
OUTPUT_DIR = "ai_engine/pothole_annotated_results"
ARTIFACTS_DIR = r"C:\Users\PC\.gemini\antigravity\brain\72338e59-c6a0-4588-9d01-655474afdf53\annotated_images"


def run_prediction_and_annotate():
    logger.info("Initializing pothole prediction and annotation run...")
    
    # 1. Load trained YOLO model weights
    weights_path = "ai_engine/weights/best.pt"
    if not os.path.exists(weights_path):
        weights_path = "yolov8n.pt"
        logger.warning(f"best.pt not found, falling back to base {weights_path}")
        
    model = YOLO(weights_path)
    logger.info(f"Loaded YOLO weights from: {weights_path}")
    
    # Create target output dirs
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    # 2. Get all images
    img_extensions = (".jpg", ".jpeg", ".png")
    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(img_extensions)]
    
    if not image_files:
        logger.error(f"No image files found in input directory: {INPUT_DIR}")
        return
        
    logger.info(f"Found {len(image_files)} images to process.")
    
    # Color palette for damage classes: Pothole -> Red (0, 0, 255)
    box_color = (0, 0, 255)
    text_color = (255, 255, 255)
    
    summary_results = []
    
    for idx, img_file in enumerate(image_files):
        img_path = os.path.join(INPUT_DIR, img_file)
        
        # Run inference
        results = model(img_path, conf=0.25, verbose=False)
        
        # Read image using OpenCV
        img = cv2.imread(img_path)
        if img is None:
            logger.warning(f"Failed to read image: {img_path}")
            continue
            
        detections_count = 0
        
        # Parse detections
        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue
                
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0].item())
                class_id = int(box.cls[0].item())
                
                # Check class names from the model config
                class_name = model.names[class_id] if hasattr(model, "names") else "pothole"
                
                detections_count += 1
                
                # Draw thick bounding box rectangle
                cv2.rectangle(img, (x1, y1), (x2, y2), box_color, 3)
                
                # Draw label banner displaying Class Name (Confidence %)
                label = f"{class_name.upper()} {conf:.2%}"
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                
                # Ensure text box is inside image bounds
                label_y1 = max(y1 - h - 10, 0)
                cv2.rectangle(img, (x1, label_y1), (x1 + w + 10, label_y1 + h + 10), box_color, -1)
                cv2.putText(
                    img, 
                    label, 
                    (x1 + 5, label_y1 + h + 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, 
                    text_color, 
                    2, 
                    cv2.LINE_AA
                )
                
        # Save annotated image
        output_path = os.path.join(OUTPUT_DIR, img_file)
        cv2.imwrite(output_path, img)
        
        # Copy to artifacts directory
        artifact_path = os.path.join(ARTIFACTS_DIR, img_file)
        shutil.copy2(output_path, artifact_path)
        
        summary_results.append({
            "filename": img_file,
            "detections": detections_count,
            "artifact_link": f"file:///{artifact_path.replace('\\', '/')}"
        })
        
        logger.info(f"[{idx+1}/{len(image_files)}] Processed {img_file} - Detected {detections_count} potholes.")
        
    print(f"\n--- Processing Finished ---")
    print(f"Processed images: {len(summary_results)}")
    
    # Save a JSON file detailing detections
    import json
    with open(os.path.join(OUTPUT_DIR, "predictions.json"), "w") as f:
        json.dump(summary_results, f, indent=2)


if __name__ == "__main__":
    run_prediction_and_annotate()
