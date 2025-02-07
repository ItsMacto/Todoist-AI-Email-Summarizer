# Todoist AI Email Summarizer

A Python application that automatically fetches your emails with the Gmail API, generates AI-powered summaries using Gemini LLM, and creates daily task summaries in Todoist.


## Installation

1. Clone the repository:
```bash
git clone https://github.com/ItsMacto/Todoist-AI-Email-Summarizer.git
cd email-summary-manager
```
2. Set Up Your Environment and Install Dependencies:
```bash
pip install -r requirements.txt
```

3. Generate Todoist API key [here](https://www.todoist.com/help/articles/find-your-api-token-Jpzx9IIlB) and store it for set up
4. Generate Google Gemini API key [here](https://aistudio.google.com/app/apikey) and store it for set up
5. Allow access to gmail
    - Ensure you have a valid credentials.json file downloaded from the [Google Cloud Console](https://console.cloud.google.com) (with Gmail API enabled)
    - Place the credentials.json file in the project root alongside main.py.
6. Run the application and follow fill in the config:
```bash
python main.py
```

7. Optional: Set up a cron job to run the script daily at a specific time. For example, to run the script at 8:00 AM every day, add the following cron job:
```bash
0 8 * * * /usr/bin/python3 /path/to/email-summary-manager/main.py
```


## Todo
- Add support for multiple email accounts
- Better prompting and filtering for emails
- Dynamic priority level 
- Better logging
- Typing to functions 