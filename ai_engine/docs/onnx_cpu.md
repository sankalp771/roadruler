# ONNX Runtime CPU inference

Install the AI engine dependencies, then export the repository's selected
pothole checkpoint from the repository root:

```powershell
python -m pip install -r ai_engine/requirements.txt
python ai_engine/scripts/export_onnx.py --weights ai_engine/weights/pretrained_pothole.pt
```

The script writes the ONNX file under `ai_engine/weights/onnx/` (model files
are ignored by Git). To benchmark an image, add
`--benchmark-image path/to/image.jpg`; the report is the median end-to-end
`RoadDamageDetector.predict` time after warmups. This includes image decode,
pre/post-processing, and CPU inference. The 120 ms goal is hardware and
checkpoint dependent; do not trade detection quality for speed without a
labeled validation set.

If you have a verified smaller or faster checkpoint, pass it explicitly with
`--weights`. Its latency does not establish equivalent detection accuracy to
the configured default model.

The detector selects Ultralytics' ONNX Runtime CPU execution provider for
`.onnx` checkpoints. `AI_WEIGHTS_PATH` can be set to an exported ONNX file in
deployments that have installed the declared `onnxruntime` dependency.
