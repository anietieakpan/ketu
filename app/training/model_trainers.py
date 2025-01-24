# app/training/model_trainers.py

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
from typing import Dict, Any
from .base_trainer import BaseTrainer

class MakeModelTrainer(BaseTrainer):
    """Trainer for vehicle make/model classification"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.num_classes = config.get('num_classes', 1000)
        self.setup_model()
        
    def setup_model(self):
        """Setup EfficientNet model for make/model classification"""
        self.model = torchvision.models.efficientnet_v2_l(weights='IMAGENET1K_V1')
        self.model.classifier[1] = nn.Linear(
            self.model.classifier[1].in_features, 
            self.num_classes
        )
        self.model = self.model.to(self.device)
        
        # Setup training components
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config.get('learning_rate', 1e-4),
            weight_decay=self.config.get('weight_decay', 1e-2)
        )
        
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=self.config.get('epochs', 100)
        )
        
        self.criterion = nn.CrossEntropyLoss()

class ColorTrainer(BaseTrainer):
    """Trainer for vehicle color classification"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.num_colors = config.get('num_colors', 12)
        self.setup_model()
        
    def setup_model(self):
        """Setup ResNet model for color classification"""
        self.model = torchvision.models.resnet18(weights='IMAGENET1K_V1')
        self.model.fc = nn.Linear(self.model.fc.in_features, self.num_colors)
        self.model = self.model.to(self.device)
        
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config.get('learning_rate', 1e-3)
        )
        
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.1,
            patience=5
        )
        
        self.criterion = nn.CrossEntropyLoss()

class TypeTrainer(BaseTrainer):
    """Trainer for vehicle type classification"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.num_types = config.get('num_types', 8)
        self.setup_model()
        
    def setup_model(self):
        """Setup ResNet model for vehicle type classification"""
        self.model = torchvision.models.resnet34(weights='IMAGENET1K_V1')
        self.model.fc = nn.Linear(self.model.fc.in_features, self.num_types)
        self.model = self.model.to(self.device)
        
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config.get('learning_rate', 1e-3)
        )
        
        self.scheduler = optim.lr_scheduler.StepLR(
            self.optimizer,
            step_size=20,
            gamma=0.1
        )
        
        self.criterion = nn.CrossEntropyLoss()

class YearEstimator(BaseTrainer):
    """Trainer for vehicle year estimation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.setup_model()
        
    def setup_model(self):
        """Setup EfficientNet model for year regression"""
        self.model = torchvision.models.efficientnet_b0(weights='IMAGENET1K_V1')
        self.model.classifier[1] = nn.Sequential(
            nn.Linear(self.model.classifier[1].in_features, 1),
            nn.ReLU()  # Ensure positive output
        )
        self.model = self.model.to(self.device)
        
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config.get('learning_rate', 1e-3)
        )
        
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.1,
            patience=5
        )
        
        # Use MSE loss for regression
        self.criterion = nn.MSELoss()
        
    def train_epoch(self, train_loader):
        """Override to handle regression metrics"""
        self.model.train()
        total_loss = 0.0
        total_mae = 0.0
        
        pbar = tqdm(train_loader, desc="Training")
        for batch_idx, (inputs, targets) in enumerate(pbar):
            inputs = inputs.to(self.device)
            targets = targets.to(self.device).float()
            
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs.squeeze(), targets)
            
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            total_mae += torch.abs(outputs.squeeze() - targets).mean().item()
            
            pbar.set_postfix({
                'loss': total_loss / (batch_idx + 1),
                'mae': total_mae / (batch_idx + 1)
            })
            
        return {
            'loss': total_loss / len(train_loader),
            'mae': total_mae / len(train_loader)
        }