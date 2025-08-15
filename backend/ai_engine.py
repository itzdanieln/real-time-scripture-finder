from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client with the key
client = OpenAI(api_key=api_key)

def match_bible_verse(input_text):
    prompt = (
        "You are a Bible assistant. The input provided is an excerpt from a sermon. "
        "Identify statements that directly reference or paraphrase a Bible verse, and insert "
        "the corresponding chapter and verse in the original text. Do not include any explanations."
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text}
        ]
    )
    return response.choices[0].message.content