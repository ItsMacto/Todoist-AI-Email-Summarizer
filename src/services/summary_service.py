

class SummaryService:
    def compile_emails(emails):
        """
        Generate a bullet-point summary for a list of emails using an LLM.
        The LLM will determine the most relevant emails, even from non-important ones, when necessary.
        Returns a well-structured prompt for summarization.
        """
        important_emails = [email for email in emails if email.get('important')]
        regular_emails = [email for email in emails if not email.get('important')]

        prompt = """You are an advanced email summarization assistant. 
                Your task is to analyze and extract the most relevant emails from the provided list. 
                Generate a bullet-point summary of the important emails, including a quick snapshot of their content.
                Use your best judgment to determine which regular emails might also be relevant.

                **Summary Format, return this:**
                ```
                - [Sender] - Snapshot summarization [Concise idea of email in one sentence]
                - ...
                - ...
                ```

                Here are the emails to summarize:\n\n"""

        for email in important_emails:
            prompt += f"- From: {email['from']}, Subject: {email['subject']}\n  Content: {email['body']}\n"

        if regular_emails:
            prompt += "\nOther emails that may contain relevant information:\n"
            for email in regular_emails:
                prompt += f"- From: {email['from']}, Subject: {email['subject']}\n  Content: {email['body']}\n"

        return prompt