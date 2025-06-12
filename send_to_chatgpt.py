import sys
import io
import os
import re
from openai import OpenAI
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Ensure UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

console = Console()

# Load env vars
api_key = os.getenv("OPENAI_API_KEY")
slack_token = os.getenv("SLACK_BOT_TOKEN")
slack_channel = os.getenv("SLACK_CHANNEL", "#all-hackathon2025")

if not api_key:
    console.print("[bold red]Missing OPENAI_API_KEY environment variable[/]")
    sys.exit(1)

client = OpenAI(api_key=api_key)

# Regex to strip emojis from AI output
def strip_emoji(text):
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

# Prompt template
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

def notify_slack(message, log_snippet=None):
    if not slack_token:
        console.print("[yellow]Slack alert skipped: SLACK_BOT_TOKEN not set.[/]")
        return

    client_slack = WebClient(token=slack_token)
    try:
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "SmartStream Alert"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{message}*\nContact: `devops@example.com`"}
            }
        ]

        if log_snippet:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Partial Log Snippet:*"}
            })
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"```{log_snippet}```"}
            })

        client_slack.chat_postMessage(channel=slack_channel, blocks=blocks)
        console.print(f"[green]Slack alert sent to {slack_channel}.[/]")
    except SlackApiError as e:
        console.print(f"[bold red]Slack API error:[/] {e.response['error']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        console.print("[bold red]Usage: python send_to_chatgpt.py <log_file>[/]")
        sys.exit(1)

    log_path = sys.argv[1]
    if not os.path.isfile(log_path):
        console.print(f"[red]Log file not found: {log_path}[/]")
        sys.exit(1)

    with open(log_path, 'r', encoding='utf-8') as f:
        log_data = f.read()

    suggestion = get_suggestion(log_data)
    clean_suggestion = strip_emoji(suggestion)

    console.rule("SmartStream Build Analysis")
    console.print(Panel.fit(
        Markdown(clean_suggestion),
        title="Suggestion by SmartStreamBot",
        border_style="cyan",
        padding=(1, 2)
    ))

    # Save full and filtered output
    with open("chatgpt_output.txt", "w", encoding="utf-8") as f:
        f.write(clean_suggestion)

    fallback_trigger = "We couldn't automatically identify this issue"
    filtered = "\n".join([line for line in clean_suggestion.splitlines() if line.startswith(">>> Suggestion") or line.startswith("- ")])

    with open("suggestion.txt", "w", encoding="utf-8") as f:
        f.write(filtered if filtered else f">>> Suggestion: {fallback_trigger}")

    if fallback_trigger in suggestion:
        log_snippet = log_data[:400]
        notify_slack("AI could not resolve Jenkins build error", log_snippet)

