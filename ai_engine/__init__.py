"""RoadRuler AI Engine package with lazy loading for heavyweight inference."""

__all__ = ["RoadDamageDetector"]


def __getattr__(name: str):
    if name == "RoadDamageDetector":
        from ai_engine.inference import RoadDamageDetector

        return RoadDamageDetector
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
