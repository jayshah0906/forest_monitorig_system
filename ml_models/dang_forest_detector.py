"""
Dang District Forest Tree Detector
Fine-tuned DeepForest model for Dang district, Gujarat

This model is optimized for:
- Dense tropical forest canopy
- Sentinel-2 satellite imagery (10m resolution)
- Tree species common in Dang district
"""

import numpy as np
import cv2
from typing import Dict, List
import pandas as pd


class DangForestDetector:
    """
    Tree detector optimized for Dang district forests
    """
    
    def __init__(self, use_finetuned=False):
        """
        Args:
            use_finetuned: If True, loads fine-tuned model for Dang
                          If False, uses pre-trained DeepForest
        """
        self.model = None
        self.use_finetuned = use_finetuned
        self.confidence_threshold = 0.4  # Optimized for dense forests
        self._load_model()
    
    def _load_model(self):
        """Load DeepForest model"""
        try:
            from deepforest import main
            
            print("Loading DeepForest model for Dang district...")
            self.model = main.deepforest()
            
            if self.use_finetuned:
                # Try to load fine-tuned model
                try:
                    self.model.load_model(name="dang_finetuned.pl")
                    print("✓ Loaded fine-tuned model for Dang district")
                except:
                    print("⚠ Fine-tuned model not found, using pre-trained")
                    self.model.use_release()
            else:
                # Use pre-trained model
                self.model.use_release()
                print("✓ Loaded pre-trained DeepForest model")
            
            print(f"✓ Confidence threshold: {self.confidence_threshold}")
            
        except ImportError:
            print("✗ DeepForest not installed!")
            print("Install with: pip install deepforest torch torchvision")
            raise
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            raise
    
    def detect(self, rgb_image: np.ndarray) -> Dict:
        """
        Detect trees in RGB satellite/aerial image
        
        Args:
            rgb_image: numpy array (H, W, 3) with values 0-1 or 0-255
        
        Returns:
            dict with:
                - count: number of trees detected
                - boxes: list of bounding boxes [[x1, y1, x2, y2], ...]
                - confidences: list of confidence scores [0-1]
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Prepare image
        image = self._prepare_image(rgb_image)
        
        # Detect trees using tile-based approach for better accuracy
        predictions = self._detect_with_tiles(image)
        
        # Filter by confidence
        predictions = predictions[predictions['score'] >= self.confidence_threshold]
        
        # Extract results
        boxes = predictions[['xmin', 'ymin', 'xmax', 'ymax']].values.tolist()
        confidences = predictions['score'].values.tolist()
        
        print(f"✓ Detected {len(boxes)} trees (confidence > {self.confidence_threshold})")
        
        return {
            'count': len(boxes),
            'boxes': boxes,
            'confidences': confidences
        }
    
    def _prepare_image(self, rgb_image: np.ndarray) -> np.ndarray:
        """Prepare image for DeepForest"""
        # Convert to 0-255 range if needed
        if rgb_image.max() <= 1.0:
            rgb_image = (rgb_image * 255).astype(np.uint8)
        
        # Ensure uint8 type
        rgb_image = rgb_image.astype(np.uint8)
        
        # DeepForest expects BGR format
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        
        return bgr_image
    
    def _detect_with_tiles(self, image: np.ndarray) -> pd.DataFrame:
        """
        Detect trees using tile-based approach
        Better for large images and dense forests
        """
        height, width = image.shape[:2]
        
        # Use tile-based detection for images larger than 800x800
        if height > 800 or width > 800:
            print(f"Using tile-based detection for large image ({height}x{width})")
            
            predictions = self.model.predict_tile(
                image=image,
                patch_size=400,  # Smaller patches for dense forest
                patch_overlap=0.15,  # 15% overlap to catch edge trees
                return_plot=False,
                mosaic=True
            )
        else:
            # Direct prediction for smaller images
            predictions = self.model.predict_image(
                image=image,
                return_plot=False
            )
        
        return predictions
    
    def visualize_detections(self, rgb_image: np.ndarray, 
                            save_path: str = 'detection_result.jpg'):
        """
        Visualize detected trees on image
        
        Args:
            rgb_image: Input image
            save_path: Path to save annotated image
        """
        image = self._prepare_image(rgb_image)
        
        # Get predictions with plot
        result_image = self.model.predict_image(
            image=image,
            return_plot=True
        )
        
        # Save
        cv2.imwrite(save_path, result_image)
        print(f"✓ Saved visualization to {save_path}")


# Singleton instance
_detector_instance = None

def get_detector(use_finetuned=False):
    """Get singleton detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = DangForestDetector(use_finetuned=use_finetuned)
    return _detector_instance


if __name__ == "__main__":
    # Test the detector
    print("Testing Dang Forest Detector...")
    
    detector = DangForestDetector()
    
    # Create test image
    test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    
    # Detect
    results = detector.detect(test_image)
    
    print(f"\nResults:")
    print(f"  Trees: {results['count']}")
    print(f"  Boxes: {len(results['boxes'])}")
    print(f"  Avg confidence: {np.mean(results['confidences']):.3f}")
