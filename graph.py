from typing import TypedDict, Annotated, Optional

from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from filters import build_filters
from user_service import get_user, update_user
from scraper import search_schemes

from dotenv import load_dotenv
import os

load_dotenv()

# ----------------------------
# State
# ----------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    profile: dict
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
    current_profile: dict,
    message: str
) -> dict:

    prompt = f"""
    Current Profile:
    {current_profile}

    Latest User Message:
    {message}

    Extract ONLY profile information explicitly
    mentioned in the latest message.

    Rules:
    - Never guess.
    - Never infer.
    - Only update fields mentioned.
    - Return null for fields not mentioned.
    - If user corrects information, use latest value.
    """

    structured_llm = llm.with_structured_output(Profile)

    profile = structured_llm.invoke(prompt)

    return profile.model_dump(exclude_none=True)


@tool
def find_schemes(profile: dict):
    """
    Find government schemes matching a profile.
    """

    filters = build_filters(profile)

    schemes = search_schemes(filters)

    return [
        {
            "name": s["fields"].get("schemeName"),
            "description": s["fields"].get("briefDescription")
        }
        for s in schemes[:10]
    ]


@tool
def story_teller(
    profile: str,
    concept: str
) -> str:
    """
    Explain a financial concept using examples tailored to the user's profile.
    """

    prompt = f"""
    You are a friendly financial educator.

    User Profile:
    {profile}

    Concept:
    {concept}

    Explain the concept using examples relevant
    to the user's situation.

    Keep the explanation under 300 words.
    """

    response = llm.invoke(prompt)

    return response.content


tools = [
    find_schemes,
    story_teller
]

llm_with_tools = llm.bind_tools(tools)


# ----------------------------
# Nodes
# ----------------------------

def memory_node(state: State):

    user = get_user(state["user_id"])

    return {
        "profile": user
    }



def profile_node(state: State):

    last_message = state["messages"][-1].content

    updates = extract_profile(
        current_profile=state["profile"],
        message=last_message
    )

    merged_profile = {
        **state["profile"],
        **updates
    }

    return {
        "profile": merged_profile
    }

def save_profile_node(state: State):

    updates = {
        k: v
        for k, v in state["profile"].items()
        if k not in ["_id"]
    }

    update_user(
        state["user_id"],
        updates
    )

    return {}

def llm_node(state: State):

    system = f"""
    You are a helpful government scheme assistant.

    User Profile:
    {state['profile']}

    When users ask:
    - scheme recommendations
    - government benefits
    - eligibility
    - subsidies
    - scholarships

    use the find_schemes tool.

    Pass the profile shown above to the tool.
    """

    response = llm_with_tools.invoke([
        SystemMessage(content=system),
        *state["messages"]
    ])

    return {
        "messages": [response]
    }

# ----------------------------
# Graph
# ----------------------------

builder = StateGraph(State)

builder.add_node("memory", memory_node)
builder.add_node("profile", profile_node)
builder.add_node("save_profile", save_profile_node)
builder.add_node("llm", llm_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "memory")
builder.add_edge("memory", "profile")
builder.add_edge("profile", "save_profile")
builder.add_edge("save_profile", "llm")

builder.add_conditional_edges(
    "llm",
    tools_condition,
    {
        "tools": "tools",
        END: END,
    }
)

builder.add_edge("tools", "llm")

graph = builder.compile()



