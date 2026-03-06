"""
Species Classification Model
Classifies detected trees into species categories

Supports:
- Teak
- Bamboo
- Sal
- Mango
- Neem
"""

import numpy as np
from typing import List, Dict
import cv2


class SpeciesClassifier:
    """
    Species classification using CNN or spectral analysis
    """
    
    def __init__(self, model_type='spectral'):
        """
        Args:
            model_type: 'cnn' or 'spectral'
        """
        self.model_type = model_type
        self.model = None
        self.species_names = ['Teak', 'Bamboo', 'Sal', 'Mango', 'Neem']
        self._load_model()
    
    def _load_model(self):
        """Load the classification model"""
        if self.model_type == 'cnn':
            self._load_cnn_model()
        elif self.model_type == 'spectral':
            print("Using spectral-based classification")
            self.model = 'spectral'
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def _load_cnn_model(self):
        """Load CNN model for species classification"""
        try:
            import tensorflow as tf
            
            model_path = "ml_models/species_classifier.h5"
            
            try:
                self.model = tf.keras.models.load_model(model_path)
                print(f"✓ Loaded CNN model from {model_path}")
            except:
                print("⚠ Custom CNN model not found")
                print("⚠ Using spectral-based classification")
                self.model = 'spectral'
                
        except ImportError:
            print("⚠ TensorFlow not installed")
            print("⚠ Using spectral-based classification")
            self.model = 'spectral'
    
    def classify(self, rgb_image: np.ndarray, tree_detections: Dict, 
                 bounds: Dict) -> List[Dict]:
        """
        Classify species for each detected tree
        
        Args:
            rgb_image: RGB image array (H, W, 3)
            tree_detections: Output from TreeDetector with boxes
            bounds: Dict with min/max lat/lon
        
        Returns:
            List of dicts with keys: lat, lon, species, confidence
        """
        boxes = tree_detections.get('boxes', [])
        confidences = tree_detections.get('confidences', [])
        
        if len(boxes) == 0:
            return []
        
        # Get image dimensions
        height, width = rgb_image.shape[:2]
        
        # Calculate lat/lon range
        lat_range = bounds['max_lat'] - bounds['min_lat']
        lon_range = bounds['max_lon'] - bounds['min_lon']
        
        tree_list = []
        
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box
            
            # Calculate center of bounding box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            # Convert pixel coordinates to lat/lon
            lat = bounds['min_lat'] + (center_y / height) * lat_range
            lon = bounds['min_lon'] + (center_x / width) * lon_range
            
            # Crop tree image
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            tree_crop = rgb_image[y1:y2, x1:x2]
            
            # Classify species
            if self.model_type == 'cnn' and self.model != 'spectral':
                species, conf = self._classify_cnn(tree_crop)
            else:
                species, conf = self._classify_spectral(tree_crop)
            
            tree_list.append({
                'lat': float(lat),
                'lon': float(lon),
                'species': species,
                'confidence': float(conf)
            })
        
        return tree_list
    
    def _classify_cnn(self, tree_crop: np.ndarray) -> tuple:
        """Classify using CNN model"""
        try:
            # Resize to model input size
            img_resized = cv2.resize(tree_crop, (224, 224))
            
            # Normalize
            img_normalized = img_resized / 255.0
            
            # Add batch dimension
            img_batch = np.expand_dims(img_normalized, axis=0)
            
            # Predict
            predictions = self.model.predict(img_batch, verbose=0)
            
            # Get species
            species_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][species_idx])
            species = self.species_names[species_idx]
            
            return species, confidence
            
        except Exception as e:
            print(f"Error in CNN classification: {e}")
            return self._classify_spectral(tree_crop)
    
    def _classify_spectral(self, tree_crop: np.ndarray) -> tuple:
        """
        Classify using spectral characteristics
        Fallback method based on color/texture analysis
        """
        if tree_crop.size == 0:
            return np.random.choice(self.species_names), 0.7
        
        # Calculate mean RGB values
        mean_r = np.mean(tree_crop[:, :, 0])
        mean_g = np.mean(tree_crop[:, :, 1])
        mean_b = np.mean(tree_crop[:, :, 2])
        
        # Calculate texture (standard deviation)
        texture = np.std(tree_crop)
        
        # Simple rule-based classification
        # (In production, replace with actual spectral signatures)
        
        if mean_g > mean_r * 1.2 and texture > 30:
            # Dense green canopy
            species = 'Teak'
            confidence = 0.82
        elif mean_g > mean_b * 1.5 and texture < 25:
            # Light green, smooth texture
            species = 'Bamboo'
            confidence = 0.78
        elif mean_r > mean_g * 0.9 and mean_g > mean_b:
            # Reddish-brown tint
            species = 'Sal'
            confidence = 0.75
        elif mean_g > 100 and texture > 35:
            # Medium green, high texture
            species = 'Mango'
            confidence = 0.73
        else:
            species = 'Neem'
            confidence = 0.70
        
        return species, confidence


# Test function
if __name__ == "__main__":
    print("Testing TreeDetector...")
    
    detector = TreeDetector(model_type='deepforest')
    
    # Create test image
    test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    
    # Detect trees
    results = detector.detect(test_image)
    print(f"\nDetected {results['count']} trees")
    print(f"Boxes: {len(results['boxes'])}")
    print(f"Confidences: {results['confidences'][:5]}...")
