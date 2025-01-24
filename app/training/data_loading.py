# app/training/data_loading.py

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from pathlib import Path
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import json
import albumentations as A
from albumentations.pytorch import ToTensorV2
import logging

logger = logging.getLogger(__name__)

class VehicleDataset(Dataset):
    """Dataset for vehicle attribute recognition"""
    
    def __init__(self, 
                 data_dir: Path,
                 annotations_file: Path,
                 attribute_type: str,
                 transform: Optional[A.Compose] = None,
                 training: bool = True):
        """
        Initialize dataset
        
        Args:
            data_dir: Path to image directory
            annotations_file: Path to JSON annotations file
            attribute_type: Type of attribute ('make_model', 'color', 'type', 'year')
            transform: Albumentations transformations
            training: Whether this is for training
        """
        self.data_dir = Path(data_dir)
        self.attribute_type = attribute_type
        self.transform = transform
        self.training = training
        
        # Load annotations
        with open(annotations_file, 'r') as f:
            self.annotations = json.load(f)
            
        # Create class mappings for classification tasks
        if attribute_type != 'year':
            self.class_to_idx = self._create_class_mapping()
            
        # Filter valid samples
        self.samples = self._filter_valid_samples()
        
        logger.info(f"Loaded {len(self.samples)} samples for {attribute_type}")
        
    def _create_class_mapping(self) -> Dict[str, int]:
        """Create mapping from class names to indices"""
        unique_values = sorted(set(
            ann[self.attribute_type] 
            for ann in self.annotations.values()
            if self.attribute_type in ann
        ))
        return {val: idx for idx, val in enumerate(unique_values)}
        
    def _filter_valid_samples(self) -> List[Tuple[Path, Any]]:
        """Filter samples with valid annotations and existing images"""
        valid_samples = []
        
        for image_name, ann in self.annotations.items():
            image_path = self.data_dir / image_name
            
            # Check if image exists and has valid annotation
            if image_path.exists() and self.attribute_type in ann:
                if self.attribute_type == 'year':
                    target = float(ann[self.attribute_type])
                else:
                    target = self.class_to_idx[ann[self.attribute_type]]
                valid_samples.append((image_path, target))
                
        return valid_samples
        
    def __len__(self) -> int:
        return len(self.samples)
        
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        image_path, target = self.samples[idx]
        
        # Read image
        image = cv2.imread(str(image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply transforms
        if self.transform:
            transformed = self.transform(image=image)
            image = transformed['image']
            
        return image, torch.tensor(target)

class VehicleDataModule:
    """Data module for handling vehicle attribute datasets"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize data module
        
        Args:
            config: Configuration dictionary containing:
                - data_dir: Path to data directory
                - annotations_file: Path to annotations
                - attribute_type: Type of attribute
                - batch_size: Batch size
                - num_workers: Number of workers
                - image_size: Input image size
        """
        self.config = config
        self.data_dir = Path(config['data_dir'])
        self.annotations_file = Path(config['annotations_file'])
        self.attribute_type = config['attribute_type']
        self.batch_size = config.get('batch_size', 32)
        self.num_workers = config.get('num_workers', 4)
        self.image_size = config.get('image_size', 224)
        
        # Create transforms
        self.train_transform = self._create_train_transform()
        self.val_transform = self._create_val_transform()
        
    def _create_train_transform(self) -> A.Compose:
        """Create training augmentations"""
        return A.Compose([
            A.RandomResizedCrop(
                height=self.image_size,
                width=self.image_size,
                scale=(0.8, 1.0)
            ),
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(p=0.2),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            A.CoarseDropout(p=0.2),
            A.GaussNoise(p=0.2),
            ToTensorV2(),
        ])
        
    def _create_val_transform(self) -> A.Compose:
        """Create validation transforms"""
        return A.Compose([
            A.Resize(self.image_size, self.image_size),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2(),
        ])
        
    def setup(self, stage: Optional[str] = None):
        """Setup train and validation datasets"""
        if stage == 'fit' or stage is None:
            self.train_dataset = VehicleDataset(
                self.data_dir,
                self.annotations_file,
                self.attribute_type,
                transform=self.train_transform,
                training=True
            )
            
            self.val_dataset = VehicleDataset(
                self.data_dir,
                self.annotations_file,
                self.attribute_type,
                transform=self.val_transform,
                training=False
            )
            
    def train_dataloader(self) -> DataLoader:
        """Create training dataloader"""
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=True
        )
        
    def val_dataloader(self) -> DataLoader:
        """Create validation dataloader"""
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True
        )

def create_attribute_transforms(image_size: int = 224) -> Tuple[A.Compose, A.Compose]:
    """Create standard transforms for vehicle attribute recognition"""
    train_transform = A.Compose([
        A.RandomResizedCrop(height=image_size, width=image_size),
        A.HorizontalFlip(p=0.5),
        A.ShiftScaleRotate(p=0.2),
        A.OneOf([
            A.GaussNoise(p=1.0),
            A.GaussianBlur(p=1.0),
            A.MotionBlur(p=1.0),
        ], p=0.2),
        A.OneOf([
            A.OpticalDistortion(p=1.0),
            A.GridDistortion(p=1.0),
        ], p=0.2),
        A.OneOf([
            A.RandomBrightnessContrast(p=1.0),
            A.HueSaturationValue(p=1.0),
        ], p=0.2),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        ToTensorV2(),
    ])
    
    val_transform = A.Compose([
        A.Resize(height=image_size, width=image_size),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        ToTensorV2(),
    ])
    
    return train_transform, val_transform