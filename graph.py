from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()

class State(TypedDict):
    messages: list

def memory_node(state):
    return {
        "messages": state["messages"]
    }

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def llm_node(state):
    response = llm.invoke(state["messages"])

    return {
        "messages": state["messages"] + [response]
    }

def extract_profile(profile, message):

    prompt = f"""
    Current Profile:
    {profile}

    Message:
    {message}

    Extract profile information.

    Return ONLY raw JSON.

    DO NOT use markdown.
    DO NOT use ```json.
    DO NOT explain anything.

    Fields:
    name
    age
    occupation
    income
    city


    """

    response = llm.invoke(prompt)
    print("RAW RESPONSE:")
    print(response.content)
    return json.loads(response.content)

builder = StateGraph(State)

builder.add_node("memory", memory_node)
builder.add_node("llm", llm_node)

builder.add_edge(START, "memory")
builder.add_edge("memory", "llm")
builder.add_edge("llm", END)

graph = builder.compile()