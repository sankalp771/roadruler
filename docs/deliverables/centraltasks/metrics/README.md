# Model evaluation charts

Generate charts only from an independently labeled binary evaluation CSV with
`ground_truth` (0 for no damage, 1 for damage) and `confidence` (model score
from 0 to 1) columns:

```csv
ground_truth,confidence
0,0.08
1,0.92
```

Run from the repository root:

```powershell
.\backend\venv\Scripts\python.exe ai_engine\scripts\evaluate_model.py path\to\labeled_eval.csv
```

The script writes `precision_recall_curve.png` and `confusion_matrix.png` here;
the confusion matrix uses a default confidence threshold of 0.5, configurable
with `--threshold`. It rejects empty, malformed, out-of-range, or single-class
manifests. No real evaluation manifest is currently checked in, so no model
performance chart or metric is being reported yet.
