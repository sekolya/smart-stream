import sys
import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']  # Set this securely via Jenkins credentials

PROMPT_TEMPLATE = """
You are an assistant that helps developers debug their CI/CD pipeline errors.

Here is the Jenkins build log:
-------------------------------
{log_content}
-------------------------------

Provide a suggestion to fix the issue. Start your answer with >>> Suggestion:
"""

def get_suggestion(log_text):
    prompt = PROMPT_TEMPLATE.format(log_content=log_text)
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-4o" if available
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        logs = f.read()

    print(get_suggestion(logs))
