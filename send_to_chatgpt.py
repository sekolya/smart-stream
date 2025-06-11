import openai
import sys
import os

# Make sure the API key is set in the environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Missing OPENAI_API_KEY environment variable")
    sys.exit(1)

openai.api_key = api_key

PROMPT_TEMPLATE = """
You are an AI assistant helping developers debug CI/CD build failures.

Below is a Jenkins build log. Review the errors and suggest how to

