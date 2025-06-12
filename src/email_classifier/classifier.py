from .cache import redis_client
from .config import MODEL_PATH
from gpt4all import GPT4All
from datetime import timedelta
import hashlib

def hash_request(subject, sender, predefined_categories, task):
    request_string = f"{subject}|{sender}|{'|'.join(predefined_categories)}|{task}"
    return hashlib.sha256(request_string.encode()).hexdigest()

def interact_with_llm(subject, sender, predefined_categories, task):
    request_key = hash_request(subject, sender, predefined_categories, task)
    cached_response = redis_client.get(request_key)
    if cached_response:
        print("Using cached response.")
        return cached_response.decode()
    if task == "category":
        prompt = ("Categorize the following email concisely.\n\n"
                  f"Sender: '{sender}'\n"
                  f"Subject: '{subject}'\n"
                  f"Predefined Categories: {predefined_categories}\n\n"
                  "Task: Select the most relevant category from the predefined list, "
                  "or suggest a new category if none apply.\n"
                  "Output Format: 'Category: [Category]'.\n"
                  "Do not include any explanations or additional text.")
    elif task == "priority":
        prompt = ("Determine the priority of the following email on a scale of 1-10 (10 is urgent, 1 can wait):\n\n"
                  f"Sender: '{sender}'\n"
                  f"Subject: '{subject}'\n\n"
                  "Criteria:\n"
                  "- Emails from individuals have a higher priority than those from newsletters or companies.\n\n"
                  "Output Format:\n"
                  "Respond strictly in this format: 'Priority: [Priority]'.\n"
                  "Example: 'Priority: 5'.\n\n"
                  "Instructions:\n"
                  "- Do not include any explanations, comments, reasoning, or additional text. write "
                  "number between 1 to 10 only\n"
                  "- Do not write anything other than the format: 'Priority: [Priority]'.\n"
                  "- Violating this format is strictly prohibited.\n"
                  "- Ensure that the output includes only the priority value in the required format and nothing else.")
    elif task == "action":
        prompt = (f"Instructions: \n"
                  f"1. Determine if follow-up action is required for the given email.\n"
                  f"2. If 'noreply' or 'no-reply' appears in the sender or subject, no action is required.\n"
                  f"3. Action is required only if:\n"
                  f"   - The email requests an explicit response or task from you.\n"
                  f"   - The email contains time-sensitive information needing your attention.\n"
                  f"4. Tickets or reports do not require action.\n\n"
                  f"Respond strictly in this format: 'Action Required: [Yes/No]'.\n"
                  f"Do not include any extra words or explanations.\n\n"
                  f"Email Data:\n"
                  f"- Sender: '{sender}'\n"
                  f"- Subject: '{subject}")
    model = GPT4All(MODEL_PATH)
    with model.chat_session():
        output = (model.generate(prompt=prompt, max_tokens=100))
        redis_client.setex(request_key, timedelta(hours=4), output)
        return output 