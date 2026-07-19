# Detailed Daily Task Guidance — Sankalp Pandey (AI Engine & Computer Vision)

**Developer:** Sankalp Pandey  
**Domain:** AI Engine / Computer Vision / Visual Deduplication / DBSCAN Spatial Clustering / PyTorch  
**Working Directory:** `ai_engine/`

---

## Structure of Daily Guidance
Each day includes:
1. **Purpose:** Why this ML/CV module is being built and how it powers the platform.
2. **What to Do:** Detailed algorithm, data pipeline, and model implementation steps.
3. **What to Expect:** Model outputs, feature vector shapes, severity scores, cluster labels.
4. **What to Check / Valid Output:** Exact verification scripts, benchmark commands, and valid tensor/JSON outputs.

---

# Phase 1: Model Pipeline, Severity Engine & Embeddings (Days 1–7)

## Day 1: Python Environment Setup & YOLOv8 Inference Class
* **Purpose:** Establish a clean, isolated Python computer vision environment and encapsulate object detection model loading into a reusable class.
* **What to Do:**
  1. Create virtual environment inside `ai_engine/`.
  2. Install dependencies: `pip install torch torchvision ultralytics opencv-python scikit-learn pillow numpy`.
  3. Build `ai_engine/inference.py`:
     ```python
     from ultralytics import YOLO
     class RoadDamageDetector:
         def __init__(self, weights_path: str):
             self.model = YOLO(weights_path)
         def predict(self, image_path: str, conf_threshold: float = 0.25):
             results = self.model(image_path, conf=conf_threshold)
             # Extract boxes, class_ids, confidences
             return parsed_detections
     ```
* **What to Expect:** Clean object detection wrapper returning structured Python dictionaries.
* **What to Check / Valid Output:**
  ```bash
  python -m ai_engine.inference --image test_road.jpg
  ```
  *Output:* Returns valid list of detection dicts: `[{"class_name": "pothole", "confidence": 0.89, "bbox": [x1, y1, x2, y2]}]`.

---

## Day 2: Dataset Curation & Formatting Script (RDD2022)
* **Purpose:** Process the multi-country Road Damage Dataset (RDD2022) into YOLO annotation format for training.
* **What to Do:**
  1. Build dataset formatting script `ai_engine/scripts/prepare_rdd.py`.
  2. Classes mapping:
     - `0`: Pothole
     - `1`: Longitudinal Crack
     - `2`: Transverse Crack
     - `3`: Alligator Crack
     - `4`: Waterlogging
  3. Convert Pascal VOC XML bounding box annotations $(x_{\min}, y_{\min}, x_{\max}, y_{\max})$ to YOLO normalized format $(x_{\text{center}}, y_{\text{center}}, w, h)$.
  4. Create `road_damage.yaml` dataset configuration file.
* **What to Expect:** Organized dataset hierarchy in `ai_engine/data/images/` and `ai_engine/data/labels/`.
* **What to Check / Valid Output:**
  - Running `python ai_engine/scripts/prepare_rdd.py` validates 1,000+ images and outputs zero annotation format errors.

---

## Day 3: YOLOv8 Fine-Tuning & Model Weight Export
* **Purpose:** Train a custom YOLOv8 model on road damage imagery to achieve high detection precision under real-world Indian road conditions.
* **What to Do:**
  1. Execute training script `ai_engine/train.py`:
     ```python
     model = YOLO("yolov8n.pt")
     model.train(data="road_damage.yaml", epochs=25, imgsz=640, batch=16)
     ```
  2. Save best weights to `ai_engine/weights/best.pt`.
* **What to Expect:** Trained model achieving validation mAP@0.5 $>0.80$.
* **What to Check / Valid Output:**
  - Training log `results.csv` confirms mAP@0.5 score exceeds 0.80 on test validation set.

---

## Day 4: Damage Severity Calculator Engine
* **Purpose:** Algorithmic calculation of damage severity (Critical / Moderate / Minor) based on bounding box dimensions and class severity weights.
* **What to Do:**
  1. Build `ai_engine/severity.py`:
     - Calculate Bounding Box Area Ratio: $\text{Area Ratio} = \frac{(x_2 - x_1) \times (y_2 - y_1)}{\text{Image Width} \times \text{Image Height}}$.
     - Class Severity Weights: Pothole ($1.0$), Waterlogging ($0.9$), Alligator Crack ($0.7$), Longitudinal Crack ($0.4$).
     - Score Formula: $\text{Severity Score} = \min(100, \sum (\text{Area Ratio} \times 100 \times \text{Weight}))$.
     - Severity Grade Assignment:
       - Score $\ge 70 \rightarrow$ `CRITICAL`
       - $35 \le \text{Score} < 70 \rightarrow$ `MODERATE`
       - Score $< 35 \rightarrow$ `MINOR`
* **What to Expect:** Consistent numerical score (0–100) and severity level string.
* **What to Check / Valid Output:**
  - Passing a large pothole detection (25% frame area) returns `severity_score: 85.0` and `severity_level: 'CRITICAL'`.

---

## Day 5: ResNet50 Visual Embedding Vector Generator
* **Purpose:** Extract deep visual feature vectors from road damage photos to enable visual similarity comparison for duplicate detection.
* **What to Do:**
  1. Build `ai_engine/embeddings.py` using PyTorch pre-trained `torchvision.models.resnet50`.
  2. Remove final classification layer so model outputs 2048-dimensional feature vector.
  3. Preprocess image (Resize to $224 \times 224$, normalize using ImageNet mean/std).
  4. L2-normalize output embedding vector: $\hat{v} = \frac{v}{\|v\|_2}$.
* **What to Expect:** 2048-dimensional normalized floating point numpy array for any input image.
* **What to Check / Valid Output:**
  - `extract_embedding(img)` returns array of shape `(2048,)` with L2 norm equal to 1.0.

---

## Day 6: Unified Pipeline Entrypoint for Celery Worker Context
* **Purpose:** Wrap object detection, severity scoring, and embedding extraction into a single, clean function for backend worker execution.
* **What to Do:**
  1. Build `ai_engine/pipeline.py`:
     ```python
     def analyze_road_issue(image_bytes: bytes) -> dict:
         # 1. Convert bytes to OpenCV image
         # 2. Run YOLOv8 detection
         # 3. Compute Severity Score & Level
         # 4. Extract ResNet50 Embedding
         return {
             "detections": [...],
             "ai_category": primary_category,
             "severity_score": score,
             "severity_level": level,
             "embedding": embedding_list
         }
     ```
* **What to Expect:** Single function call executing complete ML inference pipeline in under 1 second.
* **What to Check / Valid Output:**
  - Execute function with test image bytes; verify dictionary returned with all expected keys present.

---

## Day 7: Phase 1 Integration Pass
* **Purpose:** Confirm AI engine operates correctly when invoked inside Utkarsh's Celery worker task.
* **What to Do:** Run integration script `python -m ai_engine.tests.test_pipeline`.
* **What to Check / Valid Output:** Pipeline processes test images with zero errors.

---

# Phase 2: Deduplication, DBSCAN Clustering & Evidence Overlays (Days 8–14)

## Day 8: Spatial-Visual Deduplication Engine
* **Purpose:** Prevent redundant complaints by comparing visual features of photos taken within a close spatial radius.
* **What to Do:**
  1. Build `ai_engine/deduplication.py`:
     - Function `compute_cosine_similarity(vec1, vec2)`: $\text{Cosine Similarity} = \frac{v_1 \cdot v_2}{\|v_1\| \|v_2\|}$.
     - Function `check_duplicate(new_embedding, candidate_embeddings, threshold=0.82)`: Returns `(is_duplicate, matched_id, max_similarity)`.
* **What to Expect:** High similarity scores ($>0.85$) for different photos of the same pothole; low similarity ($<0.40$) for different road issues.
* **What to Check / Valid Output:**
  - Test with 2 photos of the same pothole taken at different angles returns `is_duplicate = True` (Similarity: 0.88).

---

## Day 9: Deduplication Benchmark Suite
* **Purpose:** Quantify the accuracy of the deduplication engine on a ground-truth dataset.
* **What to Do:**
  1. Create benchmark script `ai_engine/benchmarks/test_dedup.py` with 50 duplicate pairs and 50 distinct pairs.
  2. Compute Precision, Recall, and F1-Score across thresholds $0.75\text{–}0.90$.
* **What to Expect:** Optimal threshold (0.82) achieving Precision $>90\%$ and Recall $>85\%$.
* **What to Check / Valid Output:**
  - Script prints benchmark table confirming Precision $\ge 90\%$.

---

## Day 10: DBSCAN Spatial Hotspot Clustering Engine
* **Purpose:** Group scattered individual complaints into geographical clusters (hotspots) for municipal maintenance planning.
* **What to Do:**
  1. Build `ai_engine/clustering.py` using `scikit-learn.cluster.DBSCAN`.
  2. Convert GPS lat/lng coordinates to radians: $\text{radians} = \text{np.radians}([lat, lng])$.
  3. Run DBSCAN with Haversine metric:
     ```python
     kms_per_radian = 6371.0088
     epsilon = 0.05 / kms_per_radian  # 50-meter radius
     db = DBSCAN(eps=epsilon, min_samples=3, metric='haversine')
     cluster_labels = db.fit_predict(coords_in_radians)
     ```
* **What to Expect:** Coordinates within 50m of each other are assigned matching non-negative cluster IDs; isolated points assigned `-1` (noise).
* **What to Check / Valid Output:**
  - Inputting 5 coordinates within 30m returns cluster labels `[0, 0, 0, 0, 0]`.

---

## Day 11: Cluster Severity & Risk Rank Summarizer
* **Purpose:** Calculate summary risk metrics for each spatial cluster to help authorities prioritize funding.
* **What to Do:**
  1. Build `ai_engine/cluster_summary.py`:
     - Compute Cluster Center (centroid latitude and longitude).
     - Compute Average Severity Score across all complaints in cluster.
     - Determine Dominant Hazard Category.
     - Tag Risk Level: Average Severity $>60 \rightarrow$ `HIGH_RISK_ZONE`.
* **What to Expect:** Structured cluster metadata object for GeoJSON export.
* **What to Check / Valid Output:**
  - Cluster containing 5 critical potholes returned as `HIGH_RISK_ZONE` with centroid coordinates.

---

## Day 12: Image Evidence Bounding Box Annotation Generator
* **Purpose:** Create visual evidence images with drawn bounding box overlays for Ward Officer review.
* **What to Do:**
  1. Build `ai_engine/annotator.py` using OpenCV (`cv2.rectangle`, `cv2.putText`).
  2. Draw thick bounding box rects around detected damage.
  3. Draw label banner displaying `Class Name (Confidence %)`.
  4. Color coding: Potholes (Red), Waterlogging (Blue), Cracks (Yellow).
  5. Save annotated image as JPEG.
* **What to Expect:** High-contrast, clear evidence JPEG saved to storage.
* **What to Check / Valid Output:**
  - Generated JPEG contains crisp bounding box overlays visible over the road damage.

---

## Day 13: Synthetic Complaint Dataset Seeder
* **Purpose:** Generate realistic geospatial complaint test data across Mumbai municipal wards to stress-test the entire platform.
* **What to Do:**
  1. Build `ai_engine/scripts/seed_data.py`.
  2. Generate 150 complaint records clustered around key locations (e.g. Thakur College, Kandivali, Malad, Andheri).
  3. Include realistic coordinates, categories, severity scores, and sample photos.
* **What to Expect:** Database populated with diverse geospatial test records.
* **What to Check / Valid Output:**
  - Running seed script completes with 150 rows inserted into Neon DB.

---

## Day 14: Phase 2 Integration Pass
* **Purpose:** Verify deduplication, DBSCAN clustering, and image annotation modules under integrated testing.
* **What to Do:** Run `python -m ai_engine.tests.test_phase2`.
* **What to Check / Valid Output:** All tests pass 100%.

---

# Phase 3: Quality Filter, Model Optimization & Verification (Days 15–21)

## Day 15: Image Quality & Blur Detection Filter
* **Purpose:** Reject invalid, blurry, or non-road uploads before processing.
* **What to Do:**
  1. Build `ai_engine/quality_filter.py`:
     - Blur Detection: Compute Laplacian variance using OpenCV `cv2.Laplacian(gray, cv2.CV_64F).var()`. If variance $<60.0$, flag as `BLURRY_IMAGE`.
     - Dark Image Check: Compute average pixel intensity. If mean $<20.0$, flag as `TOO_DARK`.
* **What to Expect:** Fast pre-filter rejecting unreadable photos in $<10\text{ms}$.
* **What to Check / Valid Output:**
  - Passing an intentionally blurred image returns `is_valid: False` and `reason: "BLURRY_IMAGE"`.

---

## Day 16: "Before & After" Repair Verification Module
* **Purpose:** Validate that a reported road damage issue has actually been repaired when an officer submits a resolution photo.
* **What to Do:**
  1. Build `ai_engine/repair_verifier.py`:
     - Compare original damage photo vs post-repair photo using ResNet feature similarity and YOLO detection.
     - If post-repair photo contains 0 detected damage boxes in the original area and background feature correlation is high $\rightarrow$ Tag `REPAIR_VERIFIED`.
* **What to Expect:** Automated verification confirming road repair completion.
* **What to Check / Valid Output:**
  - Comparing clean asphalt photo against pothole photo returns `status: "REPAIR_VERIFIED"`.

---

## Day 17: ML Model Evaluation Metrics & Chart Export
* **Purpose:** Generate quantitative evaluation charts for academic paper and dossier submission.
* **What to Do:**
  1. Build `ai_engine/evaluate.py`:
     - Compute Precision, Recall, F1-Score, Confusion Matrix, and Precision-Recall Curves across classes.
     - Plot and save charts using `matplotlib` / `seaborn` to `docs/deliverables/centraltasks/metrics/`.
* **What to Expect:** Publication-grade metric plots saved as high-resolution PNGs.
* **What to Check / Valid Output:**
  - PNG charts (`confusion_matrix.png`, `pr_curve.png`) generated in metrics directory.

---

## Day 18: ONNX Runtime Model Optimization (Fast CPU Inference)
* **Purpose:** Accelerate YOLOv8 model inference speed on CPU servers by converting to ONNX runtime format.
* **What to Do:**
  1. Export PyTorch YOLO model to ONNX:
     ```python
     model = YOLO("ai_engine/weights/best.pt")
     model.export(format="onnx", dynamic=True, simplify=True)
     ```
  2. Build ONNX inference wrapper `ai_engine/onnx_inference.py` using `onnxruntime`.
* **What to Expect:** Inference execution speed increases by $3\times$ on CPU hardware ($<120\text{ms}$ per frame).
* **What to Check / Valid Output:**
  - Benchmark script confirms ONNX execution time $<120\text{ms}$ per image.

---

## Day 19: Image Security & Magic Byte Validator
* **Purpose:** Prevent malicious file uploads disguised as images from reaching the ML pipeline.
* **What to Do:**
  1. Build `ai_engine/security_check.py`:
     - Validate Magic Bytes: JPEG (`FF D8 FF`), PNG (`89 50 4E 47`), WebP (`52 49 46 46`).
     - Inspect image dimensions using Pillow; reject files exceeding $4096 \times 4096$ pixels.
* **What to Expect:** Rejection of non-image or oversized files before decoding.
* **What to Check / Valid Output:**
  - Uploading a text file renamed to `.jpg` returns `is_secure: False`.

---

## Day 20: Celery Worker Queue Stress & Concurrency Test
* **Purpose:** Verify AI engine stability under high-concurrency complaint submission spikes.
* **What to Do:**
  1. Create stress test script `ai_engine/benchmarks/stress_test.py`.
  2. Dispatch 50 simultaneous image analysis jobs into Redis/Celery queue.
  3. Monitor CPU utilization, RAM usage, and completion rate.
* **What to Expect:** All 50 jobs processed successfully without memory leaks or worker crashes.
* **What to Check / Valid Output:**
  - Stress script reports 50/50 jobs completed with $100\%$ success rate.

---

## Day 21: Phase 3 Integration Pass
* **Purpose:** Final verification of ML quality filters, ONNX runtime, repair verifier, and stress resilience.
* **What to Do:** Run `python -m ai_engine.tests.test_phase3`.
* **What to Check / Valid Output:** All integration tests pass 100%.

---

# Phase 4: Production Tuning & Staging Deployment (Days 22–30)

## Days 22–24: Inference Memory & Model Tuning
* **Purpose:** Optimize memory footprint and ensure zero RAM leakage over long daemon execution periods.
* **What to Do:** Profile PyTorch/ONNX memory allocation, garbage collection, and model caching.

## Days 25–27: AI Engine Dockerization
* **Purpose:** Containerize the AI processing environment.
* **What to Do:** Create `ai_engine/Dockerfile` built on `python:3.10-slim` with OpenCV/PyTorch dependencies. Verify execution inside Docker container.

## Days 28–30: Final Dossier Benchmarking & Presentation Setup
* **Purpose:** Package final KPI evaluation results for academic dossier defense.
* **What to Do:** Compile final accuracy, duplicate reduction %, and resolution time savings metrics for dossier report.
