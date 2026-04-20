from pathlib import Path
import json
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

def call_llm(system_prompt: str, user_prompt: str) -> bool:

    safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

    client = genai.Client(api_key=os.getenv("API_KEY"))  

    resp = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.0,
            thinking_config=types.ThinkingConfig(include_thoughts=False, thinking_budget=0),
            safety_settings=safety_settings,
        ),
    )

    response_text = (resp.text or "")

    print(f"LLM Response: {response_text}")

    if not response_text:
        print("No response from LLM.")
        return []
    
    # Remove json code block formatting if present
    if response_text.startswith("```json"):
        try:
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        except Exception as e:
            print(f"Error parsing JSON code block from LLM: {e}")
            return []

    if response_text != []:
        try:
            json_response = json.loads(response_text)
            return json_response
        except json.JSONDecodeError as e:
            print(f"JSON loading error: {e}")
            return []
    elif response_text == []:
        return []
    
    print(f"Unexpected LLM response: {response_text}")
    return []


