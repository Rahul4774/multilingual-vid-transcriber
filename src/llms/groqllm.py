from groq import Groq
from langchain_groq import ChatGroq
import os, traceback
from dotenv import load_dotenv

class GroqModel:
    def __init__(self):
        load_dotenv()
    
    def get_model(self):
        try:
            os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
            model = ChatGroq(model_name="llama-3.3-70b-versatile")
            return model
        except Exception as e:
            print(traceback.print_exc())
            raise Exception(f"Failed to initialize Groq model: {e}")

class AudioToTextGroqModel:
    def __init__(self):
        load_dotenv()
    
    def get_model(self):
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")
            model = Groq(api_key = groq_api_key)
            return model
        except Exception as e:
            print(traceback.print_exc())
            raise Exception(f"Failed to initialize Groq model: {e}")
