# Sankalp Pandey - Deliverables & Verification Checklist
**Domain:** AI Engine / Computer Vision / Deduplication / DBSCAN Clustering / PyTorch  
**Working Directory:** `ai_engine/`

---

## Deliverables Checklist

### Phase 1: Ingestion & Model Pipeline (Days 1–7)
- [x] **Day 1:** Python ML environment setup, YOLOv8 inference wrapper class `RoadDamageDetector`.
- [x] **Day 2:** RDD2022 dataset formatting script converting annotations to YOLO format.
- [x] **Day 3:** YOLOv8 model training on road damage classes; export `best.pt`.
- [x] **Day 4:** Damage Severity Score calculator combining bounding box area ratio and class weights.
- [x] **Day 5:** ResNet50 2048-dim feature vector generator for visual duplicate matching.
- [ ] **Day 6:** Single entrypoint function `analyze_road_issue(image_bytes)` for worker context.
- [ ] **Day 7:** Phase 1 End-to-End integration test pass with backend Celery worker.

### Phase 2: Deduplication & Spatial Clustering (Days 8–14)
- [ ] **Day 8:** Spatial + visual deduplication pipeline (`check_duplicate`).
- [ ] **Day 9:** Deduplication benchmark suite on test dataset confirming $>90\%$ precision.
- [ ] **Day 10:** DBSCAN Geo-Spatial Clustering engine (`clustering.py`).
- [ ] **Day 11:** Cluster Severity Summarizer ranking spatial zones by priority.
- [ ] **Day 12:** Image Evidence Bounding Box Annotator saving annotated evidence JPEG.
- [ ] **Day 13:** Synthetic Data Generator `seed_data.py` seeding 150 test complaints across Mumbai.
- [ ] **Day 14:** Phase 2 End-to-End integration test pass.

### Phase 3: Quality Control & Model Optimization (Days 15–21)
- [ ] **Day 15:** Image Quality Filter detecting blurriness (Laplacian variance) and corruption.
- [ ] **Day 16:** "Before & After" Repair Verification module comparing pre/post repair photos.
- [ ] **Day 17:** ML evaluation charts (PR curves, Confusion Matrix) exported to deliverables.
- [ ] **Day 18:** YOLO model conversion to ONNX Runtime for fast CPU inference ($<120\text{ms}$).
- [ ] **Day 19:** Image upload magic byte validation (`FF D8 FF` for JPEG, `89 50 4E 47` for PNG).
- [ ] **Day 20:** Celery worker queue stress testing under 50 simultaneous jobs.
- [ ] **Day 21:** Phase 3 End-to-End integration test pass.

### Phase 4: Production Benchmarks & Deployment (Days 22–30)
- [ ] **Days 22–24:** Inference speed and memory usage optimization.
- [ ] **Days 25–27:** Docker containerization of AI inference worker.
- [ ] **Days 28–30:** Final KPI dossier report generation.
