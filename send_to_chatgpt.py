
import sys
import os
import openai
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from rich.console import Console
from rich.panel import Panel

console = Console()

# Load API Key from Environment
api_key = os.getenv("OPENAI_API_KEY")
slack_token = os.getenv("SLACK_BOT_TOKEN")
slack_channel = os.getenv("SLACK_CHANNEL", "#devops-alerts")

if not api_key:
    console.print("[red]Missing OPENAI_API_KEY[/]")
    sys.exit(1)

client = openai.OpenAI(api_key=api_key)

PROMPT_TEMPLATE = """
You are an AI assistant helping developers debug CI/CD build failures.

Below is a Jenkins build log. Analyze the error and suggest 2–3 possible solutions in a numbered list.

LOG:
----------------------------------------
{log_content}
----------------------------------------

>>> Suggestion:
- If you can identify the root cause, suggest specific fixes.
- If you're uncertain or no actionable solution exists, reply:
>>> Suggestion: We couldn't automatically identify this issue. Please contact your DevOps team: devops@example.com
"""

def get_suggestion(log_text):
    prompt = PROMPT_TEMPLATE.format(log_content=log_text)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

def notify_slack(message):
    if not slack_token:
        console.print("[yellow]Slack alert skipped: SLACK_BOT_TOKEN not set.[/]")
        return
    client = WebClient(token=slack_token)
    try:
        client.chat_postMessage(channel=slack_channel, text=message)
        console.print("[green]Slack alert sent.[/]")
    except SlackApiError as e:
        console.print(f"[red]Slack error:[/] {e.response['error']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        console.print("Usage: python send_to_chatgpt.py <log_file>")
        sys.exit(1)

    log_path = sys.argv[1]
    if not os.path.isfile(log_path):
        console.print(f"[red]Log file not found:[/] {log_path}")
        sys.exit(1)

    with open(log_path, 'r') as f:
        log_data = f.read()

    suggestion = get_suggestion(log_data)

    # Print nicely in terminal
    console.print(Panel.fit(suggestion, title="💡 SmartStream Suggestion"))

    # Send Slack alert if fallback response detected
    if "We couldn't automatically identify this issue" in suggestion:
        slack_message = f"""
🚨 *SmartStream Alert*:
Jenkins build failed and no specific fix was found by the AI.

Please investigate manually.

🧠 GPT Response:
