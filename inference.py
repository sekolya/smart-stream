from transformers import pipeline
from typing import Dict
from sagemaker_inference import content_types, decoder
import json

# Load model and pipeline globally for efficiency
pipe = pipeline(task="text2text-generation", model="google/flan-t5-small")

def model_fn(model_dir):
    # model_dir is ignored here because we load directly from Hugging Face Hub
    return pipe

def predict_fn(input_data: Dict, model):
    input_text = input_data.get("inputs", "")
    # Generate output from pipeline
    result = model(input_text, max_length=256, do_sample=True)[0]['generated_text']
    return {"result": result}

def input_fn(request_body, request_content_type):
    # Decode input based on content type (e.g., application/json)
    return decoder.decode(request_body, request_content_type)

def output_fn(prediction, content_type):
    # Encode output as JSON string
    return json.dumps(prediction), content_types.JSON

