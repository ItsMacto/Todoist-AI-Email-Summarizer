import google.generativeai as genai
from src.config.manager import ConfigManager
from src.utils.logger import logger

class SummaryService:
    @staticmethod
    def create_prompt(emails):
        """Generate a structured prompt for email summarization."""
        important_emails = [email for email in emails if email.get('important')]
        regular_emails = [email for email in emails if not email.get('important')]

        prompt = """You are an advanced email summarization assistant. 
                Your task is to analyze and extract the most relevant emails from the provided list. 
                Generate a bullet-point summary of the important emails including key details.
                Also consider these regular emails that might contain relevant information:

                **Required Format:**
                ```
                - [Sender] - [Concise 1-sentence summary]
                - ...
                - ...
                ```
        Important Emails:\n"""
        
        for email in important_emails:
            prompt += f"\nFrom: {email['from']}\nSubject: {email['subject']}\nContent: {email['body']}\n"

        if regular_emails:
            prompt += "\nPotential Relevant Regular Emails:\n"
            for email in regular_emails:
                prompt += f"\nFrom: {email['from']}\nSubject: {email['subject']}\n"

        prompt += "\nProvide a focused summary following the required format:"
        return prompt


    
    def call_gemini(prompt):
        """
        Call the Gemini 2.0 Flash API (gemini-2.0-flash-001) with the given prompt
        and return the text summary.
        """
        # Load configuration to retrieve the Gemini API key
        config = ConfigManager().load_config()
        gemini_api_key = config.get("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.error("Gemini API key not configured. Please add GEMINI_API_KEY to your config.json.")
            return None
        
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash-001') 

        try:
            response = model.generate_content(prompt)
            if response.text:
                return response.text
            else:
                logger.warning("Gemini API returned an empty response.")
                return None
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None

