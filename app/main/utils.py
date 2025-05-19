# app/main/utils.py
import os
import joblib
import json
import pandas as pd
import numpy as np # np is imported here
from tensorflow.keras.models import load_model
from flask import current_app

# --- Global variables to hold loaded artifacts ---
# Initialize them to None. They will be loaded on first use.
_preprocessor = None
_model = None
_feature_list = []
_artifacts_loaded = False
_artifacts_load_error = None # Store any loading error


def load_artifacts():
    """Loads artifacts if not already loaded. Requires app context."""
    global _preprocessor, _model, _feature_list, _artifacts_loaded, _artifacts_load_error

    # If already loaded or failed previously, return status
    if _artifacts_loaded:
        return True
    if _artifacts_load_error:
        # If a previous load attempt failed, raise the stored error again
        # This prevents repeated failed load attempts within the same process
        raise _artifacts_load_error

    print("--- Attempting to load artifacts... ---")
    try:
        # Access config via current_app (requires app context)
        artifacts_dir = current_app.config['ARTIFACTS_DIR']
        preprocessor_file = current_app.config['PREPROCESSOR_FILE']
        model_file = current_app.config['MODEL_FILE']
        feature_list_file = current_app.config['FEATURE_LIST_FILE']

        preprocessor_path = os.path.join(artifacts_dir, preprocessor_file)
        model_path = os.path.join(artifacts_dir, model_file)
        feature_list_path = os.path.join(artifacts_dir, feature_list_file)

        # Check existence first
        if not os.path.exists(preprocessor_path):
            raise FileNotFoundError(f"Preprocessor not found at {preprocessor_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        if not os.path.exists(feature_list_path):
            raise FileNotFoundError(f"Feature list not found at {feature_list_path}")

        # Load the artifacts
        _preprocessor = joblib.load(preprocessor_path)
        _model = load_model(model_path)
        with open(feature_list_path, 'r') as f:
            _feature_list = json.load(f)

        if _preprocessor and _model and _feature_list:
            _artifacts_loaded = True
            print("--- Artifacts Loaded Successfully ---")
            if _model: _model.summary(print_fn=print) # Print summary on successful load
            return True
        else:
             # This case might be redundant if FileNotFoundError covers missing files
             raise RuntimeError("Failed to load one or more artifacts (post-load check).")

    except Exception as e:
        _artifacts_load_error = e # Store the specific error that occurred
        print(f"CRITICAL ERROR loading artifacts: {type(e).__name__} - {e}")
        # Re-raise the error so the calling function knows loading failed
        # Wrap it in a RuntimeError for consistent handling if desired
        raise RuntimeError(f"Failed to load ML artifacts: {e}") from e


# --- Getter functions remain the same ---
def get_preprocessor():
    """Returns the loaded preprocessor, loading if necessary."""
    if not _artifacts_loaded:
        load_artifacts() # Will raise error if loading fails
    if not _preprocessor:
         # This case should ideally be caught by load_artifacts failing
         raise RuntimeError("Get Preprocessor: Preprocessor object is None after load attempt.")
    return _preprocessor

def get_model():
    """Returns the loaded model, loading if necessary."""
    if not _artifacts_loaded:
        load_artifacts()
    if not _model:
         raise RuntimeError("Get Model: Model object is None after load attempt.")
    return _model

def get_feature_list():
    """Returns the loaded feature list, loading if necessary."""
    if not _artifacts_loaded:
        load_artifacts()
    if not _feature_list:
         raise RuntimeError("Get Feature List: Feature list is empty after load attempt.")
    return _feature_list

def check_artifacts():
    """Checks if artifacts are ready (attempts load if not). Needs app context."""
    if _artifacts_loaded:
        return True
    if _artifacts_load_error: # If known error occurred previously, don't retry
        return False
    try:
        # Attempt load within the current app context
        return load_artifacts()
    except Exception as e:
         print(f"Check Artifacts: Load attempt failed - {e}")
         return False # Return False if loading fails


# --- processing functions (preprocess_data_util, perform_prediction, etc.) remain the same ---
# Ensure they use the get_* functions correctly
def preprocess_data_util(df, required_features):
    # ... uses get_preprocessor(), get_model() ...
    print("--- Starting Preprocessing (Util) ---")
    preprocessor_obj = get_preprocessor()
    model_obj = get_model() # Ensure model is loaded to check input shape later
    df_copy = df.copy()

    # --- Feature Engineering ---
    if 'timestamp' in df_copy.columns:
        try:
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'], errors='coerce')
            valid_timestamps = not df_copy['timestamp'].isnull().all()
            if valid_timestamps:
                df_copy['hour'] = df_copy['timestamp'].dt.hour.fillna(-1).astype(int)
                df_copy['day_of_week'] = df_copy['timestamp'].dt.dayofweek.fillna(-1).astype(int)
                print("Timestamp features engineered.")
            else: # All timestamps failed parsing
                if 'hour' in required_features: df_copy['hour'] = -1
                if 'day_of_week' in required_features: df_copy['day_of_week'] = -1
        except Exception as e:
            print(f"Warning: Timestamp processing error: {e}")
            if 'hour' in required_features: df_copy['hour'] = -1
            if 'day_of_week' in required_features: df_copy['day_of_week'] = -1
    else: # Timestamp column missing
        if 'hour' in required_features: df_copy['hour'] = -1
        if 'day_of_week' in required_features: df_copy['day_of_week'] = -1

    # --- Feature Selection ---
    missing_cols = [col for col in required_features if col not in df_copy.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
    df_selected = df_copy[required_features]

    # --- Preprocessing ---
    try:
        df_processed = preprocessor_obj.transform(df_selected)
        if hasattr(df_processed, "toarray"):
             df_processed = df_processed.toarray()
    except Exception as e:
        raise RuntimeError(f"Preprocessor transform error: {e}")

    # --- Reshape ---
    num_processed_features = df_processed.shape[1]
    expected_features = model_obj.input_shape[1]
    if num_processed_features != expected_features:
         raise ValueError(f"Feature mismatch: Preprocessor output={num_processed_features}, Model expects={expected_features}")
    df_reshaped = df_processed.reshape(df_processed.shape[0], num_processed_features, 1)

    print("--- Preprocessing Finished (Util) ---")
    return df_reshaped

# ... other functions like perform_prediction, analyze_results, process_uploaded_file
# should remain structurally the same, using the get_* helpers ...
def perform_prediction(data_processed):
    print("--- Performing Prediction (Util) ---")
    model_obj = get_model()
    # ... rest of prediction logic ...
    predictions_proba = model_obj.predict(data_processed)
    return predictions_proba

def analyze_results(df_original, predictions_proba):
    print("--- Analyzing Results (Util) ---")
    # ... rest of analysis logic ...
    df = df_original.copy()
    threshold = current_app.config.get('PREDICTION_THRESHOLD', 0.5)
    predictions = (predictions_proba > threshold).astype(int).flatten()
    df['is_fraud_prediction'] = predictions
    df['fraud_probability'] = predictions_proba.round(4).flatten()
    # ... calculate summary ...
    fraudulent_df = df[df['is_fraud_prediction'] == 1].copy()
    total_transactions = len(df)
    total_fraud = len(fraudulent_df)
    summary = {
        "total_transactions": total_transactions,
        "total_fraud": total_fraud,
        # ... other summary fields ...
    }
    # ... calculate detailed stats ...
    fraudulent_list = fraudulent_df.to_dict(orient='records')
    return fraudulent_list, summary


def process_uploaded_file(filepath):
    print(f"--- Processing File: {filepath} ---")
    # Ensure artifacts are loaded (will attempt lazy load here within request context)
    if not check_artifacts(): # This will call load_artifacts if needed
        raise RuntimeError("Model artifacts could not be loaded. Cannot process file.")

    feature_list = get_feature_list()
    # ... rest of process_uploaded_file ...
    df_input = pd.read_csv(filepath)
    if df_input.empty: raise ValueError("CSV empty.")
    data_ready = preprocess_data_util(df_input, feature_list)
    predictions_proba = perform_prediction(data_ready)
    fraud_list, summary_data = analyze_results(df_input, predictions_proba)
    return fraud_list, summary_data