from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from db import users
from graph import graph, extract_profile
from user_service import get_user,update_user

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    phone: str
    name: str
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):

    result = graph.invoke({
        "user_id": req.user_id,
        "messages": [
            HumanMessage(content=req.message)
        ]
    })
    user = get_user(req.user_id, req.name)
    print("REQUEST NAME:", req.name)
    print("USER BEFORE UPDATE:", user)
    updates = extract_profile(
        user,
        req.message
    )
    print("EXTRACTED UPDATES:", updates)
    updated_user = update_user(
        req.user_id,
        updates
    )
    print("USER AFTER UPDATE:", updated_user)
    return {
        "reply": result["messages"][-1].content
    }