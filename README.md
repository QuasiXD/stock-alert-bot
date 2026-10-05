# Stock Alert Bot

A small Python script that watches a US stock and sends **Telegram alerts with the latest news** when its price moves by a set percentage.

Example message:

> PLTR: 🔺5.3%
> **Palantir wins new defense contract**
>
> The company announced a multi-year agreement...

## How it works

1. Gets the last two daily closing prices from [Alpha Vantage](https://www.alphavantage.co/).
2. Calculates the percentage change between them.
3. If the change meets your threshold, fetches recent headlines from [NewsAPI](https://newsapi.org/).
4. Sends each headline and summary to you through a Telegram bot (🔺 for a rise, 🔻 for a fall).

## Project structure

```
stock-alert-bot/
├── main.py            # the script
├── requirements.txt   # Python dependencies
├── .env.example       # template for your API keys
└── .gitignore         # keeps .env and the cache out of Git
```

## Requirements

- Python 3.9+
- A free [Alpha Vantage API key](https://www.alphavantage.co/support/#api-key)
- A free [NewsAPI key](https://newsapi.org/register)
- A Telegram bot token from [@BotFather](https://t.me/BotFather) and your chat ID

## Setup

### 1. Clone and install

```bash
git clone https://github.com/QuasiXD/stock-alert-bot.git
cd stock-alert-bot
python -m venv .venv
```

Activate the virtual environment:

| OS / shell | Command |
|---|---|
| Windows (cmd) | `.venv\Scripts\activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| macOS / Linux | `source .venv/bin/activate` |

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### 2. Create a Telegram bot

1. Open **@BotFather** in Telegram and send `/newbot`. Copy the token it gives you.
2. Open your new bot and press **Start**. Bots can't message you until you do.
3. Find your chat ID by visiting `https://api.telegram.org/bot<TOKEN>/getUpdates` (use your real token, without the angle brackets) and looking for `chat.id`. Alternatively, message **@userinfobot**.

### 3. Add your keys

Copy the template and fill it in:

```bash
# Windows (cmd)
copy .env.example .env

# macOS / Linux / PowerShell
cp .env.example .env
```

Your `.env` should contain:

```
ALPHA_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_newsapi_key
BOT_ID=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

> `.env` is listed in `.gitignore`. Never commit it.

## Configuration

Edit the constants at the top of `main.py`:

| Constant | Description |
|---|---|
| `STOCK` | US ticker symbol to watch, e.g. `"PLTR"` |
| `COMPANY_NAME` | Name used to search for news. Keep it matched to `STOCK` |
| `PRICE_CHANGE_THRESHOLD` | Minimum % move that triggers an alert (`5.00` for real use, `0.00` for testing) |
| `NEWS_COUNT` | Maximum number of headlines to send |
| `REQUEST_TIMEOUT` | Seconds to wait for each API call |
| `CACHE_EXPIRY_MINS` | How long API responses are cached |

## Usage

```bash
python main.py
```

If the price change is below the threshold, the script exits without sending anything. To test the whole flow, set `PRICE_CHANGE_THRESHOLD = 0.00`, run once, then set it back.

## Scheduling

The script runs once and exits, so use a scheduler to automate it. Run it after the US market closes (4:00 PM Eastern) so it uses the final close of the day.

**Windows (Task Scheduler):** create a daily task that runs:

```
C:\path\to\.venv\Scripts\python.exe C:\path\to\main.py
```

**macOS / Linux (cron):**

```
30 21 * * 1-5 /path/to/.venv/bin/python /path/to/main.py
```

## Notes and limits

- **Alpha Vantage free tier:** about 25 requests per day. Each run uses one.
- **NewsAPI free tier:** limited history, so quiet stocks may return fewer than `NEWS_COUNT` articles, or none.
- **Rate limits:** Alpha Vantage replies with HTTP 200 and an error message when you exceed its limit. The script raises a clear error in that case.
- **Cache:** responses are stored in `app_cache.sqlite`. Delete it if a bad response gets cached.
- **Weekends and holidays:** the script compares the two most recent trading sessions.

## Troubleshooting

| Problem | Likely cause |
|---|---|
| `KeyError: 'ALPHA_API_KEY'` | `.env` is missing or not in the project folder |
| `Unexpected Alpha Vantage response` | Daily limit reached, or invalid ticker |
| `404 Not Found` from Telegram | Wrong token. Test it with `https://api.telegram.org/bot<TOKEN>/getMe` |
| `403 Forbidden: bot can't initiate conversation` | You haven't pressed **Start** on your bot |
| `No news found for ...` | NewsAPI returned no matching headlines |

## Security

- Keep `.env` and `app_cache.sqlite` out of Git.
- If a key or token is ever exposed, revoke it right away (use `/revoke` in @BotFather for the Telegram token).
