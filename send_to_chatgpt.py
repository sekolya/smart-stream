import sys
import os
from openai import OpenAI, OpenAIError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# ───────────────────────────────
# Load Environment Variables
# ───────────────────────────────
api_key = os.getenv("OPENAI_API_KEY")
slack_token = os.getenv("SLACK_BOT_TOKEN")
slack_channel = os.getenv("SLACK_CHANNEL", "#all-hackathon2025")

if not api_key:
    console.print("[bold red]❌ Missing OPENAI_API_KEY environment variable[/]")
    sys.exit(1)

client = OpenAI(api_key=api_key)

# ───────────────────────────────
# Prompt Template
# ───────────────────────────────
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
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        console.print(f"[bold red]❌ OpenAI API error:[/] {str(e)}")
        return ">>> Suggestion: We couldn't automatically identify this issue. Please contact your DevOps team: devops@example.com"

def notify_slack(message, log_snippet=None):
    if not slack_token:
        console.print("[yellow]⚠️ SLACK_BOT_TOKEN not set. Skipping Slack notification.[/]")
        return
    slack = WebClient(token=slack_token)
    try:
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🤖 SmartStream Suggestion"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{message}*\nContact: `devops@example.com`"}
            }
        ]
        if log_snippet:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"```{log_snippet}```"}
            })

        slack.chat_postMessage(channel=slack_channel, blocks=blocks)
        console.print(f"[green]✅ Sent Slack alert to [bold]{slack_channel}[/][/]")

    except SlackApiError as e:
        console.print(f"[red]Slack API error:[/] {e.response['error']}")

# ───────────────────────────────
# Main Execution
# ───────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        console.print("[bold red]Usage:[/] python send_to_chatgpt.py <log_file>")
        sys.exit(1)

    log_path = sys.argv[1]
    if not os.path.isfile(log_path):
        console.print(f"[red]Log file not found:[/] {log_path}")
        sys.exit(1)

    with open(log_path, 'r', encoding='utf-8') as f:
        log_data = f.read()

    suggestion = get_suggestion(log_data)

    # Console output: pretty and colorful
    console.rule("[bold blue]🤖 SmartStream Build Analysis")
    console.print(
        Panel.fit(
            Markdown(suggestion),
            title="💡 [bold green]Suggestion by SmartStreamBot[/]",
            border_style="cyan",
            padding=(1, 2)
        )
    )

    # Slack notification with first 500 chars of log
    notify_slack(suggestion, log_snippet=log_data[:500])

    # Write plain text for Jenkins file archiving
    with open("suggestion.txt", "w", encoding="utf-8") as f:
        f.write(suggestion)

    # Print plain text for Jenkins logs
    print(suggestion)

