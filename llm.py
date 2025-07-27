from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage
import sqlite3
import os

load_dotenv("keys.env")
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
conn = sqlite3.connect("memory.db",check_same_thread=False)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/send")
async def message(request: Request):
    data = await request.json()
    raw_messages = data.get("messages", [])

    # Convert raw messages to LangChain message objects
    messages = []
    for msg in raw_messages:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        else:
            messages.append(AIMessage(content=msg['content']))

    print(f"Received Messages: {messages}")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20", temperature=0)
    agent = create_react_agent(
        model=llm,
        tools=[],
        checkpointer=SqliteSaver(conn)
    )

    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    response = agent.invoke({"messages": messages}, config)['messages'][-1].content
    print(f"Gemini Response: {response}")

    return {"status": "success", "reply": response}
