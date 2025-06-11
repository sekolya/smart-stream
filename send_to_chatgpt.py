import sys
import os
import openai

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Missing OPENAI_API_KEY environment variable")
    sys.exit(1)

client = openai.OpenAI(api_key=api_key)

PROMPT_TEMPLATE = """
You are an AI assistant helping developers debug CI/CD build failures.

Below is a Jenkins build log. Analyze the error and suggest 2–3 possible solutions, if any.

LOG:
----------------------------------------
{log_content}
----------------------------------------

>>> Suggestion:
- If you can't identify the problem, say:
We couldn't automatically identify this issue. Please contact your DevOps team: devops@example.com

- Otherwise, list the most likely fixes like this:
1. First fix idea...
2. Second fix idea...
3. (Optional) Third fix idea...
"""

def get_suggestion(log_text):
    prompt = PROMPT_TEMPLATE.format(log_content=log_text)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    if len(

