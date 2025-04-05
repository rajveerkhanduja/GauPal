from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional, Union
import pickle
import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cattle Breeding Pair Prediction API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Path to the model file
MODEL_PATH = "model/cattle_predictor_v2.pkl"

# Global variable to store model components
model = None

# Load the model at startup
@app.on_event("startup")
async def load_model():
    try:
        global model
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        logger.info(f"Successfully loaded model from {MODEL_PATH}")
        
        # Log model structure for debugging
        if isinstance(model, dict):
            logger.info(f"Model loaded as a dictionary with keys: {list(model.keys())}")
        else:
            logger.info("Model loaded as a direct predictor object")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Could not load model: {e}")

class CattlePair(BaseModel):
    Cow: Dict[str, Any]
    Bull: Dict[str, Any]
    Same_Parents: Optional[int] = 0
    Trait_Difference: Optional[int] = None
    Genetic_Diversity: Optional[float] = None
    Fertility_Rate: Optional[float] = None
    Breeding_Success_Rate: Optional[float] = None
    Disease_Resistance_Score: Optional[float] = None
    Market_Value: Optional[int] = None
    Past_Breeding_Success: Optional[str] = None

def prepare_pair_for_prediction(pair_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepares the input data for prediction by filling in missing values
    and ensuring all required fields are present.
    """
    # Copy the data to avoid modifying the original
    processed_pair = pair_data.copy()
    
    # Fill missing values with NaN for animals
    for animal in ['Cow', 'Bull']:
        if animal in processed_pair:
            # Required fields for both animals
            required_fields = [
                'Breed', 'Age', 'Weight', 'Height', 'Health_Status', 
                'Drought_Resistance', 'Temperament', 'Genetic_Diversity_Score',
                'Fertility_Rate', 'Breeding_Success_Rate', 'Disease_Resistance_Score',
                'Market_Value', 'Disease', 'Past_Breeding_Success', 'Same_Parents'
            ]
            
            # Animal-specific required fields
            animal_specific = {
                'Cow': ['Milk_Yield'],
                'Bull': ['Mother_Milk_Yield']
            }
            
            # Ensure all base fields are present
            for field in required_fields + animal_specific.get(animal, []):
                if field not in processed_pair[animal] or processed_pair[animal][field] == '':
                    processed_pair[animal][field] = np.nan
            
            # Ensure categorical fields are processed correctly
            if isinstance(processed_pair[animal]['Health_Status'], str):
                try:
                    processed_pair[animal]['Health_Status'] = int(processed_pair[animal]['Health_Status'])
                except (ValueError, TypeError):
                    processed_pair[animal]['Health_Status'] = 0  # Default to healthy

    # Add top-level keys if missing
    top_level_keys = [
        'Same_Parents', 'Trait_Difference', 'Genetic_Diversity', 
        'Fertility_Rate', 'Breeding_Success_Rate', 'Disease_Resistance_Score',
        'Market_Value', 'Past_Breeding_Success'
    ]
    
    for key in top_level_keys:
        if key not in processed_pair or processed_pair[key] == '':
            if key == 'Same_Parents':
                processed_pair[key] = 0  # Default for Same_Parents
            elif key == 'Past_Breeding_Success':
                processed_pair[key] = np.nan  # String fields
            elif key == 'Disease_Resistance_Score':
                processed_pair[key] = np.nan  # Float fields
            else:
                processed_pair[key] = np.nan  # Integer fields
    
    # Calculate Trait_Difference if not provided
    if processed_pair['Trait_Difference'] is None or np.isnan(processed_pair['Trait_Difference']):
        try:
            # Simple difference calculation based on available traits
            cow = processed_pair['Cow']
            bull = processed_pair['Bull']
            
            traits_to_compare = ['Age', 'Weight', 'Height', 'Drought_Resistance']
            differences = []
            
            for trait in traits_to_compare:
                if trait in cow and trait in bull:
                    if not np.isnan(cow[trait]) and not np.isnan(bull[trait]):
                        differences.append(abs(cow[trait] - bull[trait]))
            
            if differences:
                processed_pair['Trait_Difference'] = sum(differences)
            else:
                processed_pair['Trait_Difference'] = 0
        except Exception as e:
            logger.warning(f"Failed to calculate Trait_Difference: {e}")
            processed_pair['Trait_Difference'] = 0
    
    return processed_pair

def predict_cattle_compatibility(input_df, model_components):
    """
    Makes predictions using the combined model components.
    
    Args:
        input_df: pandas DataFrame with the prepared input data
        model_components: Dictionary containing preprocessor and classifier
        
    Returns:
        List of prediction results
    """
    try:
        if 'preprocessor' in model_components and 'classifier' in model_components:
            # Transform the input data using the preprocessor
            X_processed = model_components['preprocessor'].transform(input_df)
            
            # Make prediction using the classifier component
            y_pred = model_components['classifier'].predict(X_processed)
            
            # Get probabilities if available
            probabilities = None
            if hasattr(model_components['classifier'], "predict_proba"):
                try:
                    proba = model_components['classifier'].predict_proba(X_processed)
                    probabilities = [float(max(prob)) for prob in proba]
                except Exception as e:
                    logger.warning(f"Could not get prediction probabilities: {e}")
            
            # Format results
            results = []
            for i in range(len(y_pred)):
                result = {"prediction": "Good Pair" if y_pred[i] == 1 else "Bad Pair"}
                if probabilities:
                    result["probability"] = probabilities[i]
                results.append(result)
                
            return results
        else:
            logger.error("Missing required model components: preprocessor or classifier")
            return None
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return None

@app.post("/predict")
async def predict(pair: CattlePair):
    try:
        # Prepare data for prediction
        processed_pair = prepare_pair_for_prediction(pair.dict())
        
        # Log the processed data
        logger.info(f"Processed data for prediction: {processed_pair}")
        
        # Flatten the processed_pair into a dictionary matching DataFrame columns
        flat_sample = {}
        for prefix, inner_dict in processed_pair.items():
            if isinstance(inner_dict, dict):
                for key, value in inner_dict.items():
                    flat_sample[f"{prefix}_{key}"] = value
            else:
                # Handle top-level keys directly
                flat_sample[prefix] = inner_dict
        
        # Convert the flattened sample to a DataFrame with a single row
        input_df = pd.DataFrame([flat_sample])
        
        # Make prediction using the helper function
        predictions = predict_cattle_compatibility(input_df, model)
        
        if predictions and len(predictions) > 0:
            result = predictions[0]  # Get the first result since we only have one input pair
            return result
        else:
            raise HTTPException(status_code=500, detail="Prediction failed")
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Serve static files
@app.on_event("startup")
async def setup_static():
    static_dir = Path("static")
    if static_dir.exists():
        app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)