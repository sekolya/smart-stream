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

Below is a Jenkins build log. Review the errors and suggest how to fix them.

LOG:
----------------------------------------
{log_content}
----------------------------------------

Only return helpful, brief suggestions. Start your answer with this exact tag:
>>> Suggestion:
"""

def get_suggestion(log_text):
    prompt = PROMPT_TEMPLATE.format(log_content=log_text)

    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-4o" if you're on GPT-4 Omni
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python send_to_chatgpt.py <log_file>")
        sys.exit(1)

    log_path = sys.argv[1]
    if not os.path.isfile(log_path):
        print(f"Log file not found: {log_path}")
        sys.exit(1)

    with open(log_path, 'r') as f:
        log_data = f.read()

    suggestion = get_suggestion(log_data)
    print(suggestion)
