"""
Best Model Training - Target 85%+ Accuracy
Using Gradient Boosting + Random Forest Ensemble
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
from pathlib import Path

print("="*70)
print("Training BEST Model - Ensemble Approach")
print("="*70)

# Load data
df = pd.read_csv('data/training/dang_ground_truth.csv')

# Engineer features
df['ndvi_squared'] = df['ndvi'] ** 2
df['ndvi_cubed'] = df['ndvi'] ** 3
df['nir_green_ratio'] = df['nir'] / (df['green'] + 0.0001)
df['vegetation_index'] = (df['nir'] - df['red']) * (df['nir'] - df['green'])
df['canopy_proxy'] = df['canopy_density'] / 100.0
df['elevation_norm'] = df['elevation_m'] / 1000.0
df['slope_norm'] = df['slope_degrees'] / 35.0

features = [
    'ndvi', 'nir', 'red', 'green', 'blue',
    'gndvi', 'nir_red_ratio', 'green_red_ratio',
    'nir_std', 'texture',
    'ndvi_squared', 'ndvi_cubed', 'nir_green_ratio', 
    'vegetation_index', 'canopy_proxy',
    'elevation_norm', 'slope_norm'
]

X = df[features].values
y = df['trees_per_hectare'].values

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\n✓ Features: {len(features)}")
print(f"✓ Training samples: {len(X_train)}")

# Create ensemble of models
print("\nTraining ensemble of 3 models...")

# Model 1: Random Forest (optimized)
rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=25,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)

# Model 2: Gradient Boosting
gb = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=7,
    learning_rate=0.05,
    random_state=42
)

# Model 3: Another Random Forest with different params
rf2 = RandomForestRegressor(
    n_estimators=200,
    max_depth=30,
    min_samples_split=3,
    max_features='log2',
    random_state=123,
    n_jobs=-1
)

# Ensemble (Voting)
ensemble = VotingRegressor([
    ('rf1', rf),
    ('gb', gb),
    ('rf2', rf2)
])

print("  Training Random Forest 1...")
rf.fit(X_train_scaled, y_train)

print("  Training Gradient Boosting...")
gb.fit(X_train_scaled, y_train)

print("  Training Random Forest 2...")
rf2.fit(X_train_scaled, y_train)

print("  Creating ensemble...")
ensemble.fit(X_train_scaled, y_train)

# Evaluate all models
print("\n" + "="*70)
print("Model Comparison:")
print("="*70)

models = {
    'Random Forest 1': rf,
    'Gradient Boosting': gb,
    'Random Forest 2': rf2,
    'Ensemble (Best)': ensemble
}

best_accuracy = 0
best_model_name = None
best_model = None

for name, model in models.items():
    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    acc = np.mean(np.abs(y_pred - y_test) / y_test <= 0.15) * 100
    
    print(f"\n{name}:")
    print(f"  MAE: {mae:.2f} trees/ha")
    print(f"  R²: {r2:.4f}")
    print(f"  Accuracy (±15%): {acc:.1f}%")
    
    if acc > best_accuracy:
        best_accuracy = acc
        best_model_name = name
        best_model = model

print("\n" + "="*70)
print(f"✓ BEST MODEL: {best_model_name}")
print(f"✓ ACCURACY: {best_accuracy:.1f}%")
print("="*70)

# Save best model
model_path = Path('ml_models/dang_forest_model.pkl')
scaler_path = Path('ml_models/dang_scaler.pkl')
features_path = Path('ml_models/feature_list.pkl')

with open(model_path, 'wb') as f:
    pickle.dump(best_model, f)
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
with open(features_path, 'wb') as f:
    pickle.dump(features, f)

print(f"\n✓ Best model saved and ready for deployment!")
print(f"✓ Expected accuracy: {best_accuracy:.1f}%")
