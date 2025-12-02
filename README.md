# 🚀 Solana Token Launch Monitoring Telegram Bot

A powerful Telegram bot for monitoring and receiving real-time alerts about new PumpFun token launches on the Solana blockchain.

## ✨ Features

### 🔔 Real-Time Token Monitoring
- **New Token Alerts**: Get instant notifications when new tokens are launched on PumpFun
- **Automatic Monitoring**: Background service checks for new tokens every 30 seconds
- **Rich Token Details**: Each alert includes price, market cap, volume, holder count, and risk assessment

### 📊 Token Analytics
- **Price Information**: USD price, market cap, and 5-minute price changes
- **Trading Activity**: 1-hour volume, swap counts, and holder statistics
- **Risk Assessment**: Wash trading detection, sniper count warnings, and creator analysis
- **Progress Tracking**: Token bonding curve progress percentage

### 🛡️ Risk Indicators
- Wash trading detection
- Sniper activity monitoring
- Creator balance rate tracking
- Top 10 holder concentration

## 📁 Project Structure

```
├── src/
│   ├── main.py                    # Application entry point
│   ├── api/
│   │   ├── client.py              # HTTP client for external API calls
│   │   └── token_api.py           # Token-related API endpoints
│   ├── config/
│   │   └── settings.py            # Environment configuration
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base_model.py          # Base database model
│   │   ├── core.py                # MongoDB connection & indexes
│   │   ├── maintenance.py         # Database maintenance utilities
│   │   ├── token_operations.py    # Token CRUD operations
│   │   └── user_operations.py     # User CRUD operations
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── callback_handlers.py   # Telegram callback handlers
│   │   ├── error_handlers.py      # Error handling
│   │   └── notification_handlers.py # Notification command handlers
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py          # Base model class
│   │   ├── token_models.py        # Token data models
│   │   ├── user_models.py         # User data models
│   │   ├── wallet_models.py       # Wallet data models
│   │   └── watchlist_models.py    # Watchlist data models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── blockchain_service.py  # Solana blockchain interactions
│   │   ├── notification_service.py # PumpFun notification service
│   │   ├── scheduler_service.py   # Background task scheduler
│   │   ├── user_service.py        # User management service
│   │   └── wallet_service.py      # Wallet analysis service
│   └── utils/
│       ├── __init__.py
│       ├── blockchain.py          # Blockchain utility functions
│       ├── formatting.py          # Number/currency formatting
│       └── token_analysis.py      # Token analysis utilities
├── requirements.txt               # Python dependencies
├── LICENSE
└── README.md
```

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.8+
- MongoDB instance
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- External API server for token data

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Solana-Token-Launch-Monitoring-Telegram-bot.git
cd Solana-Token-Launch-Monitoring-Telegram-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Telegram Bot Configuration
TELEGRAM_TOKEN=your_telegram_bot_token
ADMIN_USER_IDS=123456789,987654321

# API Configuration
API_SERVER_URL=http://localhost:8000

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=new_token_sol

# Solana Blockchain Configuration
SOL_PROVIDER_URL=https://api.mainnet-beta.solana.com
SOLANA_TOKEN_PROGRAM_ID=TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
WEB3_PROVIDER_URI_KEY=your_web3_provider_key
```

### 4. Run the Bot

```bash
python src/main.py
```

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/start_notifications` | Subscribe to new token alerts |
| `/stop_notifications` | Unsubscribe from token alerts |
| `/notifications` | Manage your notification settings |
| `/scan [address]` | Get insights about a specific token |
| `/check_tokens` | Manually trigger a token check |

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `python-telegram-bot` | Telegram Bot API wrapper |
| `pymongo` | MongoDB driver |
| `apscheduler` | Background task scheduling |
| `aiohttp` | Async HTTP client |
| `solana` | Solana SDK |
| `solders` | Solana data structures |
| `anchorpy` | Anchor framework client |
| `web3` | Web3 utilities |
| `python-dotenv` | Environment variable management |
| `requests` | HTTP library |
| `pandas` | Data manipulation |
| `qrcode` | QR code generation |
| `base58` | Base58 encoding/decoding |

## 🔔 Notification Format

When a new PumpFun token is detected, you'll receive a notification like:

```
🚀 NEW PUMPFUN TOKEN DETECTED!

💰 TOKEN_SYMBOL (Token Name)
📍 Address: <token_address>

📊 Price Info:
• Price: $0.00001234
• Market Cap: $50,000
• 5m Change: 🟢 +15.50%

📈 Trading Activity:
• 1h Volume: $10,000
• 1h Swaps: 150
• Holders: 45
• Progress: 25.5%

👤 Creator: <creator_address>

🛡️ Risk Assessment: ✅ Low Risk

⏰ Created: 2025-12-02 10:30:00 UTC
```

## 🏗️ Architecture

The bot uses a service-oriented architecture:

1. **Scheduler Service**: Runs background monitoring loop every 30 seconds
2. **Notification Service**: Checks for new tokens and sends alerts to subscribers
3. **Database Layer**: MongoDB for persistent storage of tokens, users, and subscriptions
4. **API Layer**: Communicates with external API for token data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the [MIT License](./LICENSE) - see the LICENSE file for details.
