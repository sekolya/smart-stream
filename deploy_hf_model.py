import sagemaker
from sagemaker.huggingface import HuggingFaceModel
import boto3
import time

# Define AWS and model parameters
role = "arn:aws:iam::176993091276:role/SageMakerExecutionRole"  # Or manually set your IAM role ARN
region = boto3.Session().region_name
huggingface_model = 'google/flan-t5-small'  # Or 'distilbert-base-uncased'

# Hugging Face inference script
entry_point_script = 'inference.py'

# Create HuggingFaceModel object
hf_model = HuggingFaceModel(
    model_data=None,  # Using Hugging Face Hub
    transformers_version='4.26',
    pytorch_version='1.13',
    py_version='py39',
    env={
        'HF_MODEL_ID': huggingface_model,
        'HF_TASK': 'text2text-generation',  # Use 'text-classification' if applicable
    },
    role=role,
    entry_point=entry_point_script,
    source_dir='/home/ec2-user/',  # Location of inference.py
)

# Deploy endpoint
predictor = hf_model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',  # Change if needed
    endpoint_name='log-analyzer-endpoint'
)

print(f"✅ Endpoint deployed: {predictor.endpoint_name}")
