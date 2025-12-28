# MCMXI Sopel Bot

A Sopel IRC bot with module loading verification.

## Setup

The bot runs from its own directory without system-wide installs.

1. Install dependencies using hatch:
   ```bash
   hatch env create
   ```

2. Configure the bot:
   - Edit `config.cfg` with your IRC server, channels, and owner nick

3. Run the bot:
   ```bash
   hatch run sopel -c config.cfg
   ```

This will start Sopel and you'll see it load all modules in the `modules/` directory.

