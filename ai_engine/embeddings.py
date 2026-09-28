"""
ResNet50 Visual Embedding Vector Generator.
Extracts 2048-dimensional normalized feature vectors from road damage images.
"""

import argparse
import io
import logging
import os
import sys
from typing import Union

import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ResNet50FeatureExtractor(nn.Module):
    """ResNet50 Feature Extractor without classification head."""

    def __init__(self):
        super().__init__()
        logger.info("Initializing ResNet50 Feature Extractor...")
        try:
            # Load pre-trained ResNet50 with default weights (ImageNet1K_V1)
            self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            # Strip the final classification layer by replacing it with nn.Identity
            self.model.fc = nn.Identity()
            self.model.eval()
            logger.info("ResNet50 model loaded and fc layer stripped successfully.")
        except Exception as e:
            logger.error(f"Failed to load ResNet50 model: {str(e)}")
            raise RuntimeError(f"ResNet50 initialization error: {str(e)}") from e

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extract features from input tensor.
        
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, 3, 224, 224).
            
        Returns:
            torch.Tensor: Feature tensor of shape (batch_size, 2048).
        """
        with torch.no_grad():
            return self.model(x)


# Global singleton instance of extractor
_extractor = None


def get_extractor() -> ResNet50FeatureExtractor:
    """
    Get or initialize the global ResNet50FeatureExtractor singleton instance.
    
    Returns:
        ResNet50FeatureExtractor: Extractor model instance.
    """
    global _extractor
    if _extractor is None:
        _extractor = ResNet50FeatureExtractor()
    return _extractor


def extract_embedding(image_input: Union[str, bytes, np.ndarray, Image.Image]) -> np.ndarray:
    """
    Extract a normalized 2048-dimensional visual embedding vector from an image.

    Args:
        image_input: File path (str), raw image bytes (bytes), PIL Image, or numpy array.

    Returns:
        np.ndarray: A 1D float array of shape (2048,) with L2 norm equal to 1.0.
    """
    # 1. Preprocess various input formats to PIL Image in RGB mode
    pil_img = None
    if isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise FileNotFoundError(f"Image file not found: {image_input}")
        try:
            pil_img = Image.open(image_input).convert("RGB")
        except Exception as e:
            raise ValueError(f"Failed to open image file at path {image_input}: {str(e)}")
    elif isinstance(image_input, bytes):
        try:
            pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Failed to parse image bytes: {str(e)}")
    elif isinstance(image_input, Image.Image):
        pil_img = image_input.convert("RGB")
    elif isinstance(image_input, np.ndarray):
        try:
            # OpenCV stores images in BGR; convert to RGB
            rgb_img = cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_img)
        except Exception as e:
            raise ValueError(f"Failed to process numpy array image input: {str(e)}")
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    # 2. Define ImageNet standard resize, tensor conversion, and normalization transforms
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # 3. Apply transformations and add batch dimension
    input_tensor = preprocess(pil_img)
    input_batch = input_tensor.unsqueeze(0)  # Shape: (1, 3, 224, 224)

    # 4. Perform forward pass to extract visual embedding
    extractor = get_extractor()
    with torch.no_grad():
        features = extractor(input_batch)  # Shape: (1, 2048)

    # 5. Flatten the tensor to 1D and apply L2-normalization
    features_np = features.squeeze(0).cpu().numpy()
    norm = np.linalg.norm(features_np)
    if norm > 0:
        normalized_embedding = features_np / norm
    else:
        normalized_embedding = features_np

    return normalized_embedding


def main():
    parser = argparse.ArgumentParser(description="ResNet50 Visual Embedding Vector Generator CLI")
    parser.add_argument("--image", type=str, required=True, help="Path to input road image")
    args = parser.parse_args()

    try:
        embedding = extract_embedding(args.image)
        norm = np.linalg.norm(embedding)
        print("\n--- Embedding Output ---")
        print(f"Embedding Vector Shape: {embedding.shape}")
        print(f"L2 Norm: {norm:.6f}")
        print(f"First 10 values: {embedding[:10].tolist()}")
    except Exception as e:
        logger.error(f"Failed to generate embedding: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
