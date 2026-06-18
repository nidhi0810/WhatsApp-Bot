from typing import TypedDict, Annotated, Optional
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from filters import build_filters
from user_service import get_user
from scraper import search_schemes

from dotenv import load_dotenv
import os

load_dotenv()

# ----------------------------
# State
# ----------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]


# ----------------------------
# LLM
# ----------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# ----------------------------
# Structured Profile Schema
# ----------------------------

class Profile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    income: Optional[str] = None
    city: Optional[str] = None


# ----------------------------
# Tools
# ----------------------------

def extract_profile(
    current_profile: str,
    message: str
) -> str:
    """
    Extract profile information from a user message.
    """

    prompt = f"""
    Current Profile:
    {current_profile}

    New Message:
    {message}

    Extract and update profile information.
    """

    structured_llm = llm.with_structured_output(Profile)

    profile = structured_llm.invoke(prompt)

    return profile.model_dump()


def story_teller(
    profile: str,
    concept: str
) -> str:
    """
    Explain a concept using examples from the user's profile.
    """

    prompt = f"""
    You are a financial educator.

    User Profile:
    {profile}

    Concept:
    {concept}

    Explain the concept using examples relevant to the user's profile.
    Keep it simple and practical.
    """

    response = llm.invoke(prompt)

    return response.content

@tool
def find_schemes(user_id: str):
    """
    Find government schemes for a user.
    """

    user = get_user(user_id)

    filters = build_filters(user)

    schemes = search_schemes(filters)

    return [
        {
            "name": s["fields"]["schemeName"],
            "description": s["fields"]["briefDescription"]
        }
        for s in schemes[:10]
    ]

tools = [
    extract_profile,
    find_schemes,
    story_teller
]

llm_with_tools = llm.bind_tools(tools)


# ----------------------------
# Nodes
# ----------------------------

def memory_node(state: State):
    return state


def llm_node(state: State):

    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


# ----------------------------
# Graph
# ----------------------------

builder = StateGraph(State)

builder.add_node("memory", memory_node)
builder.add_node("llm", llm_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "memory")
builder.add_edge("memory", "llm")

builder.add_conditional_edges(
    "llm",
    tools_condition,
    {
        "tools": "tools",
        END: END,
    },
)

builder.add_edge("tools", "llm")

graph = builder.compile()



