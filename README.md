# ChemiNotify
Automation tool for monitoring course availability in Cheminot application system.

## Overview

ChemiNotify automates the monitoring of course availability in the Cheminot enrollment system, using image recognition to detect open spots and sending notifications when courses become available.

## Features
- Automated login to the Cheminot system
- Course monitoring at configurable intervals
- Discord notifications when courses become available
- Automatic retry when courses are full

## Onboarding
### Prerequisites
- Tested on program "Génie logiciel"
- Tested on Windows 11
- Python
- Java

### Installation
1. Clone the repo
```
git clone https://github.com/mhd-hi/ChemiNotify.git
cd ChemiNotify
```
2. Install dependencies
```
pip install -r requirements.txt
```

### Configuration
3. Configure environment variables:
- Copy `.env.example` and rename it to `.env` 
4. Edit the .env file with your specific settings (Cheminot credentials, course, file paths, [discord webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks))

4. Run the app
```
python main.py
```

## Privacy & Legal Notice

This tool is provided for personal use only. By using ChemiNotify, you agree to the following:

- This tool runs entirely on your local machine and does not collect, store, or transmit any student data.
- No personal information is shared with any third parties or remote servers except for anonymous telemetry (random UUID only) (if consented to) and the notifications you explicitly configure.
- This tool is not affiliated with or endorsed by any educational institution or the developers of the ChemiNot system.