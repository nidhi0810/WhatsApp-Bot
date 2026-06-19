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

    # Basic Details
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    income: Optional[str] = None

    # Education / Employment
    occupation: Optional[str] = None
    employmentStatus: Optional[str] = None
    isStudent: Optional[bool] = None

    # Social
    caste: Optional[str] = None
    minority: Optional[bool] = None

    # Residence
    residence: Optional[str] = None

    # Family
    maritalStatus: Optional[str] = None

    # Financial
    isBpl: Optional[bool] = None
    dbtScheme: Optional[bool] = None

    # Government / Special Categories
    isGovEmployee: Optional[bool] = None
    disability: Optional[bool] = None
    disabilityPercentage: Optional[int] = None
    isEconomicDistress: Optional[bool] = None

    # Scheme Preferences
    schemeCategory: Optional[str] = None
    benefitTypes: Optional[str] = None


# ----------------------------
# Tools
# ----------------------------

def extract_profile(
    current_profile: str,
    message: str
) -> dict:
    """
    Extract profile information from a user message.
    """
    print("EXTRACT PROFILE CALLED")

    prompt = f"""
    Current Profile:
    {current_profile}

    New Message:
    {message}

    Extract only the profile fields that can be inferred from the new message.
    Leave unknown fields as null.
    """

    structured_llm = llm.with_structured_output(Profile)

    profile = structured_llm.invoke(prompt)

    # Remove None values so we don't overwrite existing data
    updates = {
        k: v
        for k, v in profile.model_dump().items()
        if v is not None
    }

    return updates

@tool
def find_schemes(
    user_id: str,
    current_profile: str,
    message: str
):
    """
    Find government schemes for a user.
    """

    print("=" * 50)
    print("FIND SCHEMES CALLED")
    print("USER ID =", user_id)

    # Get current user from DB
    user = get_user(user_id)

    print("USER FROM DB =", user)

    # Extract latest profile updates
    updates = extract_profile(
        current_profile=current_profile,
        message=message
    )

    print("UPDATES =", updates)

    # Merge updates into user profile
    merged_user = {
        **user,
        **updates
    }

    print("MERGED USER =", merged_user)

    # Optional: persist merged profile
    users.update_one(
        {"userId": user_id},
        {"$set": updates}
    )

    filters = build_filters(merged_user)

    print("FILTERS =", filters)

    schemes = search_schemes(filters)

    print("SCHEMES FOUND =", len(schemes))

    return [
        {
            "name": scheme["fields"].get("schemeName"),
            "description": scheme["fields"].get("briefDescription")
        }
        for scheme in schemes[:10]
    ]

    
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



