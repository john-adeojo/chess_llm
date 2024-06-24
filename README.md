
# Lichess LLM Bot Setup Guide

## Prerequisites

1. **Lichess Account**:
   - Create a Lichess account here: [Lichess](https://lichess.org/)
   - Ensure this account has not played any games if you intend to use it as a bot.

2. **Lichess API Token**:
   - Create a Lichess API token here: [Lichess API Token](https://lichess.org/account/oauth/token/create?)
   - Ensure the token is enabled to "Play games with the bot API".

3. **Anaconda**:
   - You need a virtual environment to run this project. Anaconda is recommended.
   - Download Anaconda here: [Anaconda](https://www.anaconda.com/blog/productionizing-and-deploying-data-science-projects)

## Setup

### 1. Create your Anaconda virtual environment

If you're using Anaconda, follow these steps:

1. Open your Anaconda PowerShell and run:
   ```sh
   conda create -n chess_env python=3.11 pip
   ```

2. Activate the virtual environment by running:
   ```sh
   conda activate chess_env
   ```

### 2. Clone the Repository

1. Select a file location and run:
   ```sh
   git clone https://github.com/john-adeojo/chess_llm.git
   ```

2. Change your directory to the `lichess-bot` folder by running:
   ```sh
   cd lichess-bot
   ```

3. Install all dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### 3. Set up your Lichess bot

1. Open the project in your IDE of choice (e.g., VS Code).
2. Open the `config.yml` file and change the `token` value on line 1 to your Lichess token.

### 4. API Keys

To run the script using a single LLM-agent (GPT-4 by default), you will need an OpenAI API key.

1. Navigate to the `llm_agents` folder and then to `api_keys`.
2. Enter your OpenAI API key where prompted.
3. If you wish to use the Mixture of Agents option, you must also enter a Claude API key.

### 5. Upgrade to a Bot Account

In your PowerShell, ensure your current working directory is `lichess-bot`. Then run:
```sh
python lichess-bot.py -u
```
**Note:**If step 5 doesn't work the first time you run it, wait a moment and run it again!

### 6. Run your Bot

You can run your Lichess bot by running:
```sh
python lichess-bot.py -v
```
You may omit the `-v` option if you prefer a less verbose output. Verbosity will help with `debugging.

### 7. Challenge your Bot

Once your bot is online, you can challenge it against a computer or a human online player through the Lichess interface.

---
