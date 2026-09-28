"""Export YOLO weights to ONNX and optionally measure CPU inference latency."""
import argparse
import shutil
import statistics
import sys
import time
from pathlib import Path

from ultralytics import YOLO

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


def export_model(weights: Path, output_dir: Path, image_size: int = 640) -> Path:
    if not weights.is_file():
        raise FileNotFoundError(f"YOLO weights not found: {weights}")
    if image_size < 32:
        raise ValueError("image_size must be at least 32 pixels")
    output_dir.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(weights))
    exported = model.export(
        format="onnx",
        imgsz=image_size,
        device="cpu",
        dynamic=False,
        simplify=False,
        opset=17,
    )
    exported_path = Path(exported)
    if not exported_path.is_file() or exported_path.suffix.lower() != ".onnx":
        raise RuntimeError(f"Ultralytics did not produce an ONNX file: {exported_path}")
    target = output_dir / f"{weights.stem}.onnx"
    if exported_path.resolve() != target.resolve():
        shutil.copy2(exported_path, target)
    return target


def benchmark_cpu(detector, image, warmup: int = 5, runs: int = 30) -> float:
    if warmup < 0 or runs < 1:
        raise ValueError("warmup must be non-negative and runs must be positive")
    for _ in range(warmup):
        detector.predict(image)
    durations = []
    for _ in range(runs):
        started = time.perf_counter()
        detector.predict(image)
        durations.append((time.perf_counter() - started) * 1000)
    return statistics.median(durations)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, default=Path("ai_engine/weights/pretrained_pothole.pt"))
    parser.add_argument("--output-dir", type=Path, default=Path("ai_engine/weights/onnx"))
    parser.add_argument("--image-size", type=int, default=640)
    parser.add_argument("--benchmark-image", type=Path)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--target-ms", type=float, default=120.0)
    args = parser.parse_args()

    artifact = export_model(args.weights, args.output_dir, args.image_size)
    print(f"ONNX artifact: {artifact}")
    if args.benchmark_image:
        from ai_engine.inference import RoadDamageDetector

        detector = RoadDamageDetector(str(artifact))
        latency = benchmark_cpu(detector, str(args.benchmark_image), args.warmup, args.runs)
        print(f"CPU median inference: {latency:.2f} ms ({args.runs} measured runs, after {args.warmup} warmups)")
        print(f"Target <{args.target_ms:g} ms:", "PASS" if latency < args.target_ms else "NOT MET")


if __name__ == "__main__":
    main()
