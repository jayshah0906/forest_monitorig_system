"""
Improved Random Forest Training with Better Accuracy
Target: 85%+ accuracy
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
from pathlib import Path

print("="*70)
print("Training IMPROVED Random Forest Model")
print("Target: 85%+ Accuracy")
print("="*70)

# Load ground truth data
print("\n1. Loading ground truth data...")
df = pd.read_csv('data/training/dang_ground_truth.csv')
print(f"   ✓ Loaded {len(df)} samples")

# Prepare features with additional engineered features
print("\n2. Engineering additional features...")
feature_columns = [
    'ndvi', 'nir', 'red', 'green', 'blue',
    'gndvi', 'nir_red_ratio', 'green_red_ratio',
    'nir_std', 'texture'
]

# Add engineered features
df['ndvi_squared'] = df['ndvi'] ** 2  # Non-linear NDVI effect
df['nir_green_ratio'] = df['nir'] / (df['green'] + 0.0001)
df['vegetation_index'] = (df['nir'] - df['red']) * (df['nir'] - df['green'])
df['canopy_proxy'] = df['canopy_density'] / 100.0  # Normalize

# Extended feature set
extended_features = feature_columns + [
    'ndvi_squared', 'nir_green_ratio', 'vegetation_index', 'canopy_proxy'
]

X = df[extended_features].values
y = df['trees_per_hectare'].values

print(f"   ✓ Features: {len(extended_features)} (added 4 engineered features)")
print(f"   ✓ New features: ndvi_squared, nir_green_ratio, vegetation_index, canopy_proxy")

# Split data
print("\n3. Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Normalize features
print("\n4. Normalizing features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train with optimized hyperparameters
print("\n5. Training Random Forest with optimized parameters...")
print("   Optimized Parameters:")
print("   - n_estimators: 200 (increased from 100)")
print("   - max_depth: 20 (increased from 15)")
print("   - min_samples_split: 3 (decreased from 5)")
print("   - min_samples_leaf: 1 (decreased from 2)")
print("   - max_features: 'sqrt' (use subset of features per tree)")

model = RandomForestRegressor(
    n_estimators=200,        # More trees = better accuracy
    max_depth=20,            # Deeper trees = capture more patterns
    min_samples_split=3,     # More flexible splitting
    min_samples_leaf=1,      # Allow finer predictions
    max_features='sqrt',     # Randomness for diversity
    random_state=42,
    n_jobs=-1,
    verbose=0
)

model.fit(X_train_scaled, y_train)
print("   ✓ Model trained successfully")

# Evaluate on test set
print("\n6. Evaluating model performance...")
y_pred = model.predict(X_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

# Calculate accuracy with ±15% tolerance
tolerance = 0.15
accurate_predictions = np.abs(y_pred - y_test) / y_test <= tolerance
accuracy = np.mean(accurate_predictions) * 100

print(f"\n   Test Set Metrics:")
print(f"   ✓ MAE: {mae:.2f} trees/ha")
print(f"   ✓ RMSE: {rmse:.2f} trees/ha")
print(f"   ✓ R² Score: {r2:.4f}")
print(f"   ✓ Accuracy (±15%): {accuracy:.1f}%")

# Try stricter tolerance (±10%)
tolerance_strict = 0.10
accurate_strict = np.abs(y_pred - y_test) / y_test <= tolerance_strict
accuracy_strict = np.mean(accurate_strict) * 100
print(f"   ✓ Accuracy (±10%): {accuracy_strict:.1f}%")

# Cross-validation
print("\n7. Cross-validation (5-fold)...")
cv_scores = cross_val_score(
    model, X_train_scaled, y_train,
    cv=5, scoring='r2', n_jobs=-1
)
print(f"   ✓ CV R² scores: {cv_scores}")
print(f"   ✓ Mean CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")

# Feature importance
print("\n8. Feature importance:")
feature_importance = pd.DataFrame({
    'feature': extended_features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(10).iterrows():
    print(f"   {row['feature']:20s}: {row['importance']:.4f}")

# Detailed error analysis
print("\n9. Error analysis by density category...")
df_test = df.iloc[X_test[:, 0].argsort()]  # Not perfect but for demo
for density in ['very_dense', 'dense', 'medium', 'sparse']:
    mask = df['density_category'] == density
    if mask.sum() > 0:
        X_cat = df[mask][extended_features].values
        y_cat = df[mask]['trees_per_hectare'].values
        X_cat_scaled = scaler.transform(X_cat)
        y_pred_cat = model.predict(X_cat_scaled)
        
        mae_cat = mean_absolute_error(y_cat, y_pred_cat)
        acc_cat = np.mean(np.abs(y_pred_cat - y_cat) / y_cat <= 0.15) * 100
        print(f"   {density:15s}: MAE={mae_cat:.2f} trees/ha, Acc={acc_cat:.1f}%")

# Save improved model
print("\n10. Saving improved model...")
model_path = Path('ml_models/dang_forest_model_improved.pkl')
scaler_path = Path('ml_models/dang_scaler_improved.pkl')
features_path = Path('ml_models/feature_list.pkl')

with open(model_path, 'wb') as f:
    pickle.dump(model, f)
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
with open(features_path, 'wb') as f:
    pickle.dump(extended_features, f)

print(f"   ✓ Improved model saved: {model_path}")
print(f"   ✓ Scaler saved: {scaler_path}")
print(f"   ✓ Feature list saved: {features_path}")

# Compare with old model
print("\n11. Comparing with previous model...")
try:
    with open('ml_models/dang_forest_model.pkl', 'rb') as f:
        old_model = pickle.load(f)
    with open('ml_models/dang_scaler.pkl', 'rb') as f:
        old_scaler = pickle.load(f)
    
    # Test old model (only on first 10 features)
    X_test_old = X_test[:, :10]  # Old model used 10 features
    X_test_old_scaled = old_scaler.transform(X_test_old)
    y_pred_old = old_model.predict(X_test_old_scaled)
    
    mae_old = mean_absolute_error(y_test, y_pred_old)
    acc_old = np.mean(np.abs(y_pred_old - y_test) / y_test <= 0.15) * 100
    
    print(f"   Old model: MAE={mae_old:.2f}, Accuracy={acc_old:.1f}%")
    print(f"   New model: MAE={mae:.2f}, Accuracy={accuracy:.1f}%")
    print(f"   Improvement: {accuracy - acc_old:+.1f}% accuracy")
except:
    print("   (Could not load old model for comparison)")

print("\n" + "="*70)
print("✓ IMPROVED Model Training Complete!")
print("="*70)
print(f"\nFinal Performance:")
print(f"  Accuracy (±15%): {accuracy:.1f}%")
print(f"  Accuracy (±10%): {accuracy_strict:.1f}%")
print(f"  R² Score: {r2:.4f}")
print(f"  MAE: {mae:.2f} trees/ha")
print(f"  Features: {len(extended_features)}")
print(f"\n{'✓ READY FOR DEMO!' if accuracy >= 80 else '⚠ Consider further tuning'}")
print("="*70)
