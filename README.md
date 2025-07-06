# ChemiNotify
> _Bot for monitoring course availability in Cheminot application system._

## Overview

Uses image recognition to detect open spots and sends notifications when courses become available.

**Note:** This tool only works during active registration periods when the Cheminot system allows course enrollment. It will not function outside of these periods, which is normal behavior.

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
On Powershell:
```
pip install -r requirements.txt
Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata/raw/main/fra.traineddata" -OutFile "C:\Program Files\Tesseract-OCR\tessdata\fra.traineddata"
```

### Configuration
3. Configure environment variables:
- Copy `.env.example` and rename it to `.env` 
4. Edit the .env file with your specific settings (Cheminot credentials, course, file paths, [discord webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks))

5. Run the app
```
python main.py
```

## Privacy & Legal Notice

This tool is provided for personal use only. By using ChemiNotify, you agree to the following:

- This tool runs entirely on your local machine and does not collect, store, or transmit any student data.
- This tool is not affiliated with or endorsed by any educational institution or the developers of the ChemiNot system.