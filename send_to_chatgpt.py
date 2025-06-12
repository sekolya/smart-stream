import sys
import os
import openai
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()

# ─────────────────────────────────────────────────────────────────────────────
# 🔐 Load Environment Variables
# ─────────────────────────────────────────────────────────────────────────────
api_key = os.getenv("OPENAI_API_KEY")
slack_token = os.getenv("SLACK_BOT_TOKEN")
slack_channel = os.getenv("SmartStreamBot", "#devops-alerts")

if not api_key:
    console.print("[bold red]❌ Missing OPENAI_API_KEY environment variable[/]")
    sys.exit(1)

client = openai.OpenAI(api_key=api_key)

# ─────────────────────────────────────────────────────────────────────────────
# 📄 Prompt Template
# ─────────────────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────────────
# 💡 Ask OpenAI for Suggestions
# ─────────────────────────────────────────────────────────────────────────────
def get_suggestion(log_text):
    prompt = PROMPT_TEMPLATE.format(log_content=log_text)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

# ─────────────────────────────────────────────────────────────────────────────
# 📣 Notify Slack (Optional)
# ─────────────────────────────────────────────────────────────────────────────
def notify_slack(message):
    if not slack_token:
        console.print("[yellow]⚠️ Slack alert skipped: SLACK_BOT_TOKEN not set.[/]")
        return

    client = WebClient(token=slack_token)
    try:
        response = client.chat_postMessage(channel=slack_channel, text=message)
        console.print(f"[green]✅ Slack alert sent to [bold]{slack_channel}[/].[/]")
    except SlackApiError as e:
        console.print(f"[bold red]Slack API error:[/] {e.response['error']}")

# ─────────────────────────────────────────────────────────────────────────────
# 🚀 Main Script
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        console.print("[bold red]Usage:[/] python send_to_chatgpt.py <log_file>")
        sys.exit(1)

    log_path = sys.argv[1]

    if not os.path.isfile(log_path):
        console.print(f"[red]Log file not found:[/] {log_path}")
        sys.exit(1)

    with open(log_path, 'r') as f:
        log_data = f.read()

    suggestion = get_suggestion(log_data)

    # ✨ Display AI suggestion in terminal with color panel
    console.rule("[bold blue]:robot: SmartStream Build Analysis")
    console.print(Panel.fit(
        Markdown(suggestion),
        title=":bulb: [bold green]Suggestion by ChatGPT[/]",
        border_style="cyan",
        padding=(1, 2)
    ))

    # 🛑 Fallback trigger detection for Slack
    fallback_trigger = "We couldn't automatically identify this issue"

    if fallback_trigger in suggestion:
        log_snippet = log_data[:400]
        syntax = Syntax(log_snippet, "bash", theme="monokai", line_numbers=True)

        slack_message = (
            ":rotating_light: *SmartStream Alert: Unresolved CI/CD Failure*\n"
            "The AI could not automatically resolve the Jenkins build error.\n"
            ">>> Suggestion: Please contact your DevOps team at devops@example.com\n\n"
            "*Partial Log Snippet:*"
        )

        notify_slack(slack_message + f"\n```{log_snippet}```")
