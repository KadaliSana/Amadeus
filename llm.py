from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from stt import STT
import os

# Initialize STT
stt = STT()
prompt_text = stt.listen()

print(f"Transcribed Text: {prompt_text}")

os.environ['HF_HUB_CACHE'] = "/home/kadalisana/Amadeus/models/cache"
os.environ['HF_HOME'] = "/home/kadalisana/Amadeus/models"
os.environ["GOOGLE_API_KEY"]="AIzaSyADGgdcpX1pQuRNisY0cGeZBpjnqvw5jnE"

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20",temperature=0)

# Create a HumanMessage
message = HumanMessage(content=prompt_text)

# Get response from Gemini
response = llm.invoke([message])

print(f"Gemini Response: {response.content}")
