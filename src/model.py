from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os

load_dotenv()

def get_model():

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_ENDPOINT")

    return OpenAIChatCompletionsModel(
        model="gpt-4.1",
        openai_client=AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    )