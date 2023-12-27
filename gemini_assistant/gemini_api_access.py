import os
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from setup.gemini_tools import gemini_tools

def start_chat():
    vertexai.init(project=os.environ["PROJECT_ID"] , location=os.environ["LOCATION"])
    model = GenerativeModel("gemini-pro", tools=[gemini_tools])
    chat = model.start_chat()
    return chat



