#!/usr/bin/env python3
"""
Model Training Script using MCP Data
Demonstrates how to use the same MCP server for model training
"""

import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

from src.mcp_client.python_client import PythonMCPClient


class SolanaPricePredictor:
    """Train a model to predict Solana price movements"""
    
    def __init__(self):
        self.client = PythonMCPClient()
        self.model = None
        self.feature_names = []
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
    async def collect_training_data(self, num_samples: int = 10):
        """
        Collect training data by making multiple MCP calls
        
        Args:
            num_samples: Number of data points to collect
            
        Returns:
            DataFrame with features and target
        """
        print(f"Collecting {num_samples} samples of training data...")
        
        data_points = []
        
        for i in range(num_samples):
            print(f"  Sample {i+1}/{num_samples}...")
            
            # Get current SOL price
            sol_price = await self.client.get_solana_price()
            
            if sol_price:
                # Create features (in real scenario, would include more market data)
                features = {
                    'hour': datetime.now().hour,
                    'day_of_week': datetime.now().weekday(),
                    'price': sol_price,
                    'log_price': np.log(sol_price) if sol_price > 0 else 0,
                    'sample_index': i  # Temporal feature
                }
                
                data_points.append(features)
                
                # Small delay between samples
                if i < num_samples - 1:
                    await asyncio.sleep(2)
        
        # Convert to DataFrame
        df = pd.DataFrame(data_points)
        
        # Create synthetic target (price change)
        # In real scenario, would wait and get actual future prices
        df['target'] = df['price'].shift(-1) - df['price']
        df = df.dropna()  # Remove last row with NaN target
        
        print(f"Collected {len(df)} valid training samples")
        return df
    
    async def train(self, num_samples: int = 20):
        """
        Train the price prediction model
        
        Args:
            num_samples: Number of training samples to collect
        """
        print("=== Starting Model Training ===")
        
        # Collect training data via MCP
        df = await self.collect_training_data(num_samples)
        
        # Save training data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv(f"models/training_data_{timestamp}.csv", index=False)
        print(f"Saved training data to models/training_data_{timestamp}.csv")
        
        # Prepare features and target
        feature_cols = ['hour', 'day_of_week', 'price', 'log_price', 'sample_index']
        X = df[feature_cols]
        y = df['target']
        
        self.feature_names = feature_cols
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        print("\nTraining Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print("\n=== Model Evaluation ===")
        print(f"Mean Squared Error: {mse:.6f}")
        print(f"R² Score: {r2:.4f}")
        
        # Feature importance
        print("\n=== Feature Importance ===")
        for feat, imp in zip(self.feature_names, self.model.feature_importances_):
            print(f"{feat}: {imp:.4f}")
        
        # Save model
        model_path = f"models/sol_predictor_{timestamp}.pkl"
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names,
            'metrics': {'mse': mse, 'r2': r2},
            'timestamp': timestamp
        }, model_path)
        print(f"\nModel saved to {model_path}")
        
        return self.model
    
    async def predict_next_price(self):
        """
        Use the trained model to predict the next price movement
        """
        if self.model is None:
            print("No model loaded. Please train first.")
            return None
        
        # Get current data
        current_price = await self.client.get_solana_price()
        
        if current_price is None:
            print("Failed to get current price")
            return None
        
        # Prepare features
        features = pd.DataFrame([{
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'price': current_price,
            'log_price': np.log(current_price) if current_price > 0 else 0,
            'sample_index': 0  # Latest sample
        }])
        
        # Make prediction
        predicted_change = self.model.predict(features[self.feature_names])[0]
        predicted_price = current_price + predicted_change
        
        print(f"\n=== Price Prediction ===")
        print(f"Current SOL Price: ${current_price:.2f}")
        print(f"Predicted Change: ${predicted_change:.2f}")
        print(f"Predicted Next Price: ${predicted_price:.2f}")
        
        return {
            'current_price': current_price,
            'predicted_change': predicted_change,
            'predicted_price': predicted_price,
            'timestamp': datetime.now().isoformat()
        }


class ModelScheduler:
    """Schedule and manage model training jobs"""
    
    def __init__(self):
        self.predictor = SolanaPricePredictor()
        self.schedule_file = Path("models/training_schedule.json")
        self.load_schedule()
    
    def load_schedule(self):
        """Load training schedule from file"""
        if self.schedule_file.exists():
            with open(self.schedule_file) as f:
                self.schedule = json.load(f)
        else:
            self.schedule = {
                'last_training': None,
                'training_interval_hours': 24,
                'auto_retrain': True
            }
    
    def save_schedule(self):
        """Save training schedule to file"""
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedule, f, indent=2)
    
    async def check_and_train(self):
        """Check if training is needed and execute if necessary"""
        last_training = self.schedule.get('last_training')
        interval_hours = self.schedule.get('training_interval_hours', 24)
        
        needs_training = False
        
        if last_training is None:
            needs_training = True
            print("No previous training found. Starting initial training...")
        else:
            last_time = datetime.fromisoformat(last_training)
            time_since = datetime.now() - last_time
            
            if time_since > timedelta(hours=interval_hours):
                needs_training = True
                print(f"Last training was {time_since.total_seconds()/3600:.1f} hours ago. Time to retrain!")
        
        if needs_training:
            await self.predictor.train(num_samples=20)
            self.schedule['last_training'] = datetime.now().isoformat()
            self.save_schedule()
            print("Training completed and schedule updated.")
        else:
            print("Model is up to date. No training needed.")
    
    async def run_continuous(self):
        """Run continuous training schedule"""
        print("Starting continuous model training scheduler...")
        
        while True:
            try:
                await self.check_and_train()
                
                # Make a prediction with the latest model
                prediction = await self.predictor.predict_next_price()
                
                # Save prediction
                if prediction:
                    predictions_file = Path("models/predictions.jsonl")
                    with open(predictions_file, 'a') as f:
                        f.write(json.dumps(prediction) + '\n')
                
                # Wait before next check
                print(f"\nWaiting 1 hour before next check...")
                await asyncio.sleep(3600)  # 1 hour
                
            except KeyboardInterrupt:
                print("\nScheduler stopped by user.")
                break
            except Exception as e:
                print(f"Error in scheduler: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error


async def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════╗
    ║   Solana Price Prediction Model Training  ║
    ║         Using MCP Data Gateway            ║
    ╚═══════════════════════════════════════════╝
    """)
    
    print("Choose an option:")
    print("1. Train new model")
    print("2. Make prediction with existing model")
    print("3. Run continuous scheduler")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        predictor = SolanaPricePredictor()
        await predictor.train(num_samples=30)
        
    elif choice == "2":
        predictor = SolanaPricePredictor()
        
        # Load latest model
        models = sorted(Path("models").glob("sol_predictor_*.pkl"))
        if models:
            latest_model = models[-1]
            print(f"Loading model: {latest_model}")
            
            model_data = joblib.load(latest_model)
            predictor.model = model_data['model']
            predictor.feature_names = model_data['feature_names']
            
            await predictor.predict_next_price()
        else:
            print("No trained models found. Please train first.")
            
    elif choice == "3":
        scheduler = ModelScheduler()
        await scheduler.run_continuous()
    
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    asyncio.run(main())