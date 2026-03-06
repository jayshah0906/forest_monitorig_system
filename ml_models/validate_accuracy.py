"""
Accuracy Validation Script
Tests model accuracy on Dang district images
"""

import numpy as np
import cv2
from pathlib import Path
from dang_forest_detector import DangForestDetector


def validate_on_test_set():
    """
    Validate model accuracy on test images
    """
    print("="*60)
    print("Model Accuracy Validation")
    print("="*60)
    
    # Load detector
    detector = DangForestDetector(use_finetuned=False)
    
    # Test images directory
    test_dir = Path("test_images")
    
    if not test_dir.exists():
        print(f"\n⚠ Test images directory not found: {test_dir}")
        print("\nCreate test_images/ folder and add:")
        print("1. 5-10 Dang district forest images")
        print("2. ground_truth.json with manual tree counts")
        print("\nExample ground_truth.json:")
        print("""{
  "image1.jpg": 150,
  "image2.jpg": 200,
  "image3.jpg": 180
}""")
        return
    
    # Load ground truth
    import json
    ground_truth_file = test_dir / "ground_truth.json"
    
    if not ground_truth_file.exists():
        print(f"\n⚠ Ground truth file not found: {ground_truth_file}")
        return
    
    with open(ground_truth_file) as f:
        ground_truth = json.load(f)
    
    # Validate each image
    results = []
    
    for image_name, true_count in ground_truth.items():
        image_path = test_dir / image_name
        
        if not image_path.exists():
            print(f"⚠ Image not found: {image_path}")
            continue
        
        # Load image
        image = cv2.imread(str(image_path))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect trees
        detections = detector.detect(image_rgb)
        predicted_count = detections['count']
        
        # Calculate accuracy
        error = abs(true_count - predicted_count)
        accuracy = (1 - error / true_count) * 100 if true_count > 0 else 0
        
        results.append({
            'image': image_name,
            'ground_truth': true_count,
            'predicted': predicted_count,
            'error': error,
            'accuracy': accuracy
        })
        
        print(f"\n{image_name}:")
        print(f"  Ground truth: {true_count}")
        print(f"  Predicted: {predicted_count}")
        print(f"  Error: {error}")
        print(f"  Accuracy: {accuracy:.1f}%")
    
    # Overall statistics
    if results:
        avg_accuracy = np.mean([r['accuracy'] for r in results])
        
        print("\n" + "="*60)
        print("OVERALL RESULTS")
        print("="*60)
        print(f"Images tested: {len(results)}")
        print(f"Average accuracy: {avg_accuracy:.1f}%")
        
        if avg_accuracy >= 85:
            print(f"\n✓ SUCCESS! Accuracy target achieved (>85%)")
        else:
            print(f"\n⚠ Below target. Current: {avg_accuracy:.1f}%, Target: 85%")
            print("\nSuggestions:")
            print("1. Adjust confidence threshold")
            print("2. Use tile-based detection")
            print("3. Fine-tune on Dang samples")


if __name__ == "__main__":
    validate_on_test_set()
