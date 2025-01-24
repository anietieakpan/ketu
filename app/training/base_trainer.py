# app/training/base_trainer.py

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Any, Optional, List, Tuple
import logging
from pathlib import Path
import mlflow
import json
from tqdm import tqdm

logger = logging.getLogger(__name__)

class BaseTrainer:
    """Base class for all vehicle attribute trainers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_dir = Path(config.get('model_dir', 'app/models/vehicle'))
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Training components
        self.model: Optional[nn.Module] = None
        self.optimizer: Optional[optim.Optimizer] = None
        self.scheduler: Optional[optim.lr_scheduler._LRScheduler] = None
        self.criterion: Optional[nn.Module] = None
        
        # MLflow setup
        mlflow.set_experiment(config.get('experiment_name', 'vehicle_recognition'))
        
    def save_model(self, name: str) -> None:
        """Save model weights and config"""
        if self.model is None:
            raise ValueError("No model to save")
            
        model_path = self.model_dir / f"{name}.pth"
        config_path = self.model_dir / f"{name}_config.json"
        
        # Save model weights
        torch.save(self.model.state_dict(), model_path)
        
        # Save model config
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
            
        logger.info(f"Saved model to {model_path}")
        
    def load_model(self, name: str) -> None:
        """Load model weights and config"""
        model_path = self.model_dir / f"{name}.pth"
        config_path = self.model_dir / f"{name}_config.json"
        
        if not model_path.exists():
            raise FileNotFoundError(f"No model found at {model_path}")
            
        # Load model weights
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        
        # Load config if exists
        if config_path.exists():
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
                
        logger.info(f"Loaded model from {model_path}")
        
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc="Training")
        for batch_idx, (inputs, targets) in enumerate(pbar):
            inputs, targets = inputs.to(self.device), targets.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            
            # Calculate accuracy for classification tasks
            if isinstance(self.criterion, (nn.CrossEntropyLoss, nn.BCEWithLogitsLoss)):
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
                
                pbar.set_postfix({
                    'loss': total_loss / (batch_idx + 1),
                    'acc': 100. * correct / total
                })
            else:
                pbar.set_postfix({'loss': total_loss / (batch_idx + 1)})
                
        metrics = {
            'loss': total_loss / len(train_loader),
            'accuracy': 100. * correct / total if total > 0 else 0
        }
        
        return metrics
        
    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate model"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, targets in tqdm(val_loader, desc="Validating"):
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                
                total_loss += loss.item()
                
                # Calculate accuracy for classification tasks
                if isinstance(self.criterion, (nn.CrossEntropyLoss, nn.BCEWithLogitsLoss)):
                    _, predicted = outputs.max(1)
                    total += targets.size(0)
                    correct += predicted.eq(targets).sum().item()
                    
        metrics = {
            'val_loss': total_loss / len(val_loader),
            'val_accuracy': 100. * correct / total if total > 0 else 0
        }
        
        return metrics
        
    def train(self, 
              train_loader: DataLoader, 
              val_loader: DataLoader,
              num_epochs: int,
              model_name: str) -> Dict[str, List[float]]:
        """Full training loop with validation"""
        history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        best_val_loss = float('inf')
        
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(self.config)
            
            for epoch in range(num_epochs):
                # Train
                train_metrics = self.train_epoch(train_loader)
                
                # Validate
                val_metrics = self.validate(val_loader)
                
                # Update learning rate
                if self.scheduler is not None:
                    self.scheduler.step()
                
                # Log metrics
                mlflow.log_metrics({
                    **train_metrics,
                    **val_metrics
                }, step=epoch)
                
                # Save best model
                if val_metrics['val_loss'] < best_val_loss:
                    best_val_loss = val_metrics['val_loss']
                    self.save_model(f"{model_name}_best")
                
                # Update history
                history['train_loss'].append(train_metrics['loss'])
                history['train_acc'].append(train_metrics['accuracy'])
                history['val_loss'].append(val_metrics['val_loss'])
                history['val_acc'].append(val_metrics['val_accuracy'])
                
                logger.info(f"Epoch {epoch+1}/{num_epochs}:")
                logger.info(f"Train Loss: {train_metrics['loss']:.4f}, Acc: {train_metrics['accuracy']:.2f}%")
                logger.info(f"Val Loss: {val_metrics['val_loss']:.4f}, Acc: {val_metrics['val_accuracy']:.2f}%")
        
        return history

        
        
        