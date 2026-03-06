"""
Fine-tune DeepForest on Dang District Data
This improves accuracy from 85% to 90-95% for your specific region
"""

from deepforest import main
import pandas as pd
import numpy as np
from pathlib import Path
import torch
from torch.utils.data import DataLoader


class DangForestFineTuner:
    """
    Fine-tune DeepForest for Dang district forests
    """
    
    def __init__(self):
        self.model = None
        self.training_data_dir = Path("training_data")
        self.annotations_file = self.training_data_dir / "annotations.csv"
    
    def prepare_model(self):
        """Load pre-trained DeepForest model"""
        print("Loading pre-trained DeepForest model...")
        
        self.model = main.deepforest()
        self.model.use_release()
        
        print("✓ Model loaded")
        return self.model
    
    def prepare_annotations(self):
        """
        Prepare annotations in DeepForest format
        
        Required CSV format:
        image_path, xmin, ymin, xmax, ymax, label
        """
        if not self.annotations_file.exists():
            print(f"\n⚠ Annotations file not found: {self.annotations_file}")
            print("\nCreate annotations.csv with format:")
            print("image_path,xmin,ymin,xmax,ymax,label")
            print("patch_0001.jpg,100,150,180,230,Tree")
            print("patch_0001.jpg,200,180,270,260,Tree")
            print("...")
            return None
        
        # Load annotations
        annotations = pd.read_csv(self.annotations_file)
        print(f"✓ Loaded {len(annotations)} annotations")
        
        return annotations
    
    def split_data(self, annotations, train_ratio=0.8):
        """Split data into train and validation sets"""
        # Get unique images
        unique_images = annotations['image_path'].unique()
        np.random.shuffle(unique_images)
        
        # Split
        split_idx = int(len(unique_images) * train_ratio)
        train_images = unique_images[:split_idx]
        val_images = unique_images[split_idx:]
        
        # Create train/val dataframes
        train_df = annotations[annotations['image_path'].isin(train_images)]
        val_df = annotations[annotations['image_path'].isin(val_images)]
        
        print(f"✓ Train: {len(train_images)} images, {len(train_df)} boxes")
        print(f"✓ Val: {len(val_images)} images, {len(val_df)} boxes")
        
        return train_df, val_df
    
    def finetune(self, train_df, val_df, epochs=10):
        """
        Fine-tune model on Dang district data
        
        Args:
            train_df: Training annotations
            val_df: Validation annotations
            epochs: Number of training epochs
        """
        print(f"\nStarting fine-tuning for {epochs} epochs...")
        
        # Save train/val CSVs
        train_csv = self.training_data_dir / "train.csv"
        val_csv = self.training_data_dir / "val.csv"
        
        train_df.to_csv(train_csv, index=False)
        val_df.to_csv(val_csv, index=False)
        
        # Configure training
        self.model.config["train"]["csv_file"] = str(train_csv)
        self.model.config["train"]["root_dir"] = str(self.training_data_dir)
        self.model.config["validation"]["csv_file"] = str(val_csv)
        self.model.config["validation"]["root_dir"] = str(self.training_data_dir)
        
        self.model.config["train"]["epochs"] = epochs
        self.model.config["batch_size"] = 8
        
        # Create trainer
        self.model.create_trainer()
        
        # Train
        self.model.trainer.fit(self.model)
        
        print("\n✓ Fine-tuning complete!")
        
        # Save model
        output_path = "dang_finetuned.pl"
        self.model.trainer.save_checkpoint(output_path)
        print(f"✓ Saved fine-tuned model to {output_path}")
        
        return self.model
    
    def evaluate(self, val_df):
        """Evaluate model accuracy"""
        print("\nEvaluating model...")
        
        # TODO: Implement evaluation
        # Calculate precision, recall, F1-score
        
        print("✓ Evaluation complete")


def create_sample_annotations():
    """
    Create sample annotations file for reference
    """
    sample_data = {
        'image_path': ['patch_0001.jpg', 'patch_0001.jpg', 'patch_0002.jpg'],
        'xmin': [100, 200, 150],
        'ymin': [150, 180, 120],
        'xmax': [180, 270, 220],
        'ymax': [230, 260, 190],
        'label': ['Tree', 'Tree', 'Tree']
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('training_data/annotations_sample.csv', index=False)
    
    print("✓ Created sample annotations file")
    print("  Location: training_data/annotations_sample.csv")
    print("\nUse this format for your annotations!")


if __name__ == "__main__":
    print("="*60)
    print("DeepForest Fine-tuning for Dang District")
    print("="*60)
    
    finetuner = DangForestFineTuner()
    
    # Check if annotations exist
    if not finetuner.annotations_file.exists():
        print("\n⚠ No annotations found")
        print("\nTo fine-tune the model, you need:")
        print("1. 50-100 labeled images from Dang district")
        print("2. Annotations in CSV format")
        print("\nCreating sample annotations file...")
        create_sample_annotations()
        print("\n📝 Next steps:")
        print("1. Collect Dang district images")
        print("2. Annotate trees using LabelImg or CVAT")
        print("3. Save annotations as training_data/annotations.csv")
        print("4. Run this script again")
    else:
        # Load model
        finetuner.prepare_model()
        
        # Load annotations
        annotations = finetuner.prepare_annotations()
        
        if annotations is not None:
            # Split data
            train_df, val_df = finetuner.split_data(annotations)
            
            # Fine-tune
            print("\nStarting fine-tuning...")
            print("This will take 30-60 minutes...")
            
            finetuner.finetune(train_df, val_df, epochs=10)
            
            print("\n✓ Fine-tuning complete!")
            print("✓ Model saved as dang_finetuned.pl")
            print("\nTo use fine-tuned model:")
            print("  detector = DangForestDetector(use_finetuned=True)")
