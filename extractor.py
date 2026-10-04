from google import genai
from google.genai import types
from prompt import EXTRACTION_PROMPT
from schema import Receipt
import streamlit as st
from pathlib import Path 
client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

          
def extract_receipt(image_bytes:bytes,mime_type:str)->Receipt:
     image_part=types.Part.from_bytes(data=image_bytes,mime_type=mime_type)
     client=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
     response=client.models.generate_content(model="gemini-3.5-flash-lite",contents=[EXTRACTION_PROMPT,image_part],config=types.GenerateContentConfig(response_mime_type="application/json",response_schema=Receipt))
     return response.parsed 
