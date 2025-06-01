# 🤖 Discord Bot - Multi-Purpose Bot

A versatile Discord bot with various features for your server!

## 📋 Available Commands

### 🔧 Utility Commands
- `/hello` - Bot greets you
- `/ping` - Check bot latency
- `/serverinfo` - Display server information
- `/userinfo` - Display user information
- `/help` - Show available commands
- `/botinfo` - Complete bot information

### 🧮 Calculator & Tools
- `/kalkulator [operation]` - Mathematical calculator
- `/acakangka [min] [max]` - Generate random number

### 🌐 API Commands
- `/meme` - Random meme from internet
- `/animeinfo [title]` - Anime information from MAL
- `/quote` - Random inspirational quote
- `/catfact` - Random cat facts
- `/dog` - Random dog photos
- `/weather [city]` - Weather information (setup required)
- `/crypto [coin]` - Cryptocurrency prices (USD & IDR, 24h changes, market cap, volume)

**Use slash commands (/) to execute commands!**

## 🚀 How to Use the Bot

### 1. Running Commands
- Type `/` in Discord chat to see available commands
- Select the command you want to use
- Fill in required parameters (if any)
- Press Enter to execute

### 2. Usage Examples
```
/crypto bitcoin          # Check Bitcoin price
/weather Jakarta         # Check Jakarta weather
/kalkulator 10 + 5       # Calculate 10 + 5
/acakangka 1 100         # Random number 1-100
/animeinfo Naruto        # Get Naruto anime info
```

## 🔗 How to Add Bot to Your Discord Server

### Step 1: Invite Bot
1. Click bot invite link: [CLICK HERE TO INVITE BOT](https://discord.com/oauth2/authorize?client_id=1378267124669349949&permissions=414531832832&integration_type=0&scope=bot+applications.commands)
2. Select server where you want to add the bot
3. Make sure you have "Manage Server" permission
4. Check required permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Attach Files
   - Read Message History

### Step 2: Bot Setup
1. Bot will be automatically online after being added
2. Test with `/ping` command to ensure bot is working
3. Use `/help` to see all available commands

### Step 3: Permissions (Optional)
- Set role permissions if needed
- Restrict commands to specific channels
- Setup moderation according to server needs

## ⚠️ Rules & Guidelines

### 🚫 Anti-Spam Policy
**IMPORTANT:** To maintain service quality and avoid API rate limiting:

#### Usage Limits:
- **API Commands**: Maximum 5 requests per minute per user
- **General Commands**: Maximum 10 requests per minute per user
- **Cooldown**: 3 seconds between commands for same user

#### Commands with Strict Rate Limits:
- `/meme` - 1 request per 10 seconds
- `/crypto` - 1 request per 5 seconds
- `/weather` - 1 request per 10 seconds
- `/animeinfo` - 1 request per 5 seconds

#### Spam Penalties:
1. **First warning**: Bot will give a warning
2. **Repeated spam**: Temporary cooldown 1 minute
3. **Excessive spam**: Temporary blacklist 5 minutes

### 📝 Usage Rules:
1. **Don't spam commands** - Wait for bot response before next command
2. **Use as needed** - Don't abuse API calls
3. **Respect other users** - Don't flood channels with bot commands
4. **Report bugs** - Report errors to server admin

### ✅ Usage Tips:
- Use commands in dedicated bot channels if possible
- Wait for response before running another command
- Use `/help` if confused about commands
- Check bot status with `/ping` if not responding

## 🛠️ Developer Setup

### Requirements
```
Python 3.8+
aiohappyeyeballs==2.6.1
aiohttp==3.12.6
aiosignal==1.3.2
attrs==25.3.0
audioop-lts==0.2.1
discord.py==2.5.2
frozenlist==1.6.0
idna==3.10
multidict==6.4.4
propcache==0.3.1
yarl==1.20.0
```

### Installation
```bash
# Clone repository
git clone https://github.com/Rasenpai/discord-bot.git
cd BOT_DISCORD

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with tokens and API keys

# Run bot
python bot.py
```

### Environment Variables
```env
DISCORD_TOKEN=your_discord_bot_token
WEATHER_API_KEY=your_weather_api_key
# Add other API keys as needed
```

## 📞 Support & Contact

- **Bug Reports**: Create issue on GitHub repository
- **Feature Requests**: Contact server admin
- **General Help**: Use `/help` command

## 📄 License

This project uses MIT License. See `LICENSE` file for complete details.

## 🔄 Updates & Changelog

This bot receives regular feature updates. Check repository for latest changelog.

---

**Disclaimer**: This bot uses various external APIs. Availability and response time depend on third-party services used.