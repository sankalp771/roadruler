# Visual deduplication benchmark

Run the benchmark with a labeled CSV manifest containing exactly 50 duplicate
pairs and 50 distinct pairs:

```csv
image_a,image_b,is_duplicate
../data/images/val/road_a.jpg,../data/images/val/road_b.jpg,true
../data/images/val/road_a.jpg,../data/images/val/road_c.jpg,false
```

Paths are resolved relative to the manifest. Positive pairs must be two
different image files with independently verified labels; byte-identical
positive pairs are rejected. The benchmark does not invent labels or generate
synthetic pairs. It caches embeddings for repeated images and reports precision,
recall, and F1 at thresholds from 0.75 through 0.90.

```powershell
.\backend\venv\Scripts\python.exe ai_engine\benchmarks\test_dedup.py ai_engine\benchmarks\dedup_pairs.csv
```

The repository's image dataset does not currently include a labeled duplicate
pair manifest, so it cannot support a defensible precision or recall result yet.
