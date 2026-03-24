import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class CADMLModel:
    def __init__(self, model_dir='models/'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_dir = os.path.join(base_dir, model_dir)
        self.rf_path = os.path.join(self.model_dir, 'rf_classifier.pkl')
        self.nn_path = os.path.join(self.model_dir, 'nn_classifier.pkl')
        self.ensemble_path = os.path.join(self.model_dir, 'ensemble_classifier.pkl')
        self.scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        
        self.rf_model = None
        self.nn_model = None
        self.ensemble_model = None
        self.scaler = None
        self.feature_names = [
            "thickness_mm", "volume_mm3", "aspect_ratio", 
            "sa_volume_ratio", "symmetry_score"
        ]
        
        self.load_models()
        
    def load_models(self):
        if os.path.exists(self.rf_path) and os.path.exists(self.nn_path) and os.path.exists(self.ensemble_path) and os.path.exists(self.scaler_path):
            self.rf_model = joblib.load(self.rf_path)
            self.nn_model = joblib.load(self.nn_path)
            self.ensemble_model = joblib.load(self.ensemble_path)
            self.scaler = joblib.load(self.scaler_path)
        else:
            print("Models not found. Training new ones (Random Forest, Neural Network, and Ensemble)...")
            self.train_and_save()
            
    def train_and_save(self):
        """Generate a massive 10,000 synthetic design dataset and train all models, including the Ensemble."""
        np.random.seed(42)
        n_samples = 10000
        
        # Good designs (Thicker, more symmetrical, balanced)
        good_features = pd.DataFrame({
            "thickness_mm": np.random.normal(3.5, 0.8, n_samples // 2),
            "volume_mm3": np.random.normal(5000, 1000, n_samples // 2),
            "aspect_ratio": np.random.normal(2.0, 0.5, n_samples // 2),
            "sa_volume_ratio": np.random.normal(0.5, 0.1, n_samples // 2),
            "symmetry_score": np.random.normal(0.8, 0.1, n_samples // 2),
            "label": 1 # 1 = PASS
        })
        
        # Bad designs (Thin, highly asymmetrical, extreme aspect ratios)
        bad_features = pd.DataFrame({
            "thickness_mm": np.random.normal(1.2, 0.5, n_samples // 2),
            "volume_mm3": np.random.normal(1500, 500, n_samples // 2),
            "aspect_ratio": np.random.normal(8.0, 2.0, n_samples // 2),
            "sa_volume_ratio": np.random.normal(1.5, 0.3, n_samples // 2),
            "symmetry_score": np.random.normal(0.3, 0.1, n_samples // 2),
            "label": 0 # 0 = FAIL
        })
        
        # Combine and clip values
        data = pd.concat([good_features, bad_features]).reset_index(drop=True)
        data = data.clip(lower=0.1)
        data['symmetry_score'] = data['symmetry_score'].clip(upper=1.0)
        
        X = data[self.feature_names]
        y = data['label'].astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Scaler (important for Neural Network and sometimes helps Ensemble)
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # 1. Train Random Forest (Individual)
        self.rf_model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        self.rf_model.fit(X_train, y_train)
        
        # 2. Train Neural Network (MLP Individual)
        self.nn_model = MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=1500, random_state=42)
        self.nn_model.fit(X_train_scaled, y_train)
        
        # 3. Train Hybrid Enterprise Ensemble (XGBoost + RF + DL)
        # Ensemble uses scaled data so MLP works correctly inside it
        rf_est = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        nn_est = MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=1500, random_state=42)
        xgb_est = XGBClassifier(n_estimators=150, max_depth=5, learning_rate=0.1, use_label_encoder=False, eval_metric='logloss')
        
        self.ensemble_model = VotingClassifier(
            estimators=[('rf', rf_est), ('nn', nn_est), ('xgb', xgb_est)],
            voting='soft'
        )
        self.ensemble_model.fit(X_train_scaled, y_train)
        
        # Save models
        os.makedirs(self.model_dir, exist_ok=True)
        joblib.dump(self.rf_model, self.rf_path)
        joblib.dump(self.nn_model, self.nn_path)
        joblib.dump(self.ensemble_model, self.ensemble_path)
        joblib.dump(self.scaler, self.scaler_path)
        
    def predict(self, feature_dict, engine='ensemble'):
        features = []
        for feat in self.feature_names:
             features.append(feature_dict.get(feat, 0))
             
        X_input = pd.DataFrame([features], columns=self.feature_names)
        
        if engine == 'nn':
            X_scaled = self.scaler.transform(X_input)
            prediction = self.nn_model.predict(X_scaled)[0]
            prob = self.nn_model.predict_proba(X_scaled)[0]
            engine_name = "Neural Network"
        elif engine == 'ensemble':
            X_scaled = self.scaler.transform(X_input)
            prediction = self.ensemble_model.predict(X_scaled)[0]
            prob = self.ensemble_model.predict_proba(X_scaled)[0]
            engine_name = "High Accuracy Enterprise Ensemble (XGBoost+NN+RF)"
        else:
            prediction = self.rf_model.predict(X_input)[0]
            prob = self.rf_model.predict_proba(X_input)[0]
            engine_name = "Random Forest"
        
        confidence = float(max(prob))
        verdict = "PASS" if prediction == 1 else "FAIL"
        
        return {
            "verdict": verdict,
            "confidence": round(confidence * 100, 2),
            "engine_used": engine_name
        }
