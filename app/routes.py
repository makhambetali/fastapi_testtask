from fastapi import APIRouter, HTTPException,  WebSocket, WebSocketDisconnect
from bson import ObjectId
from app.database import messages_collection
from app.models import Message
import time
import asyncio

router = APIRouter()
def message_helper(message: dict) -> dict:
    message["_id"] = str(message["_id"])
    return message

@router.post("/messages/")
async def create_message(message: Message):
    message_dict = message.dict()
    new_message = await messages_collection.insert_one(message_dict)
    created_message = await messages_collection.find_one({"_id": new_message.inserted_id})

    return {"id": str(created_message["_id"])} 


@router.get("/messages/{id}")
async def get_message(id: str):
    message = await messages_collection.find_one({"_id": ObjectId(id)})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message_helper(message)

@router.get("/messages/")
async def get_messages(from_user_id: int, to_user_id: int):
    messages = messages_collection.find(
        {"from_user_id": from_user_id, "to_user_id": to_user_id}
    ).sort("publish_timestamp", -1)
    return [message_helper(msg) async for msg in messages]

@router.put("/messages/{id}")
async def update_message(id: str, updated_message: Message):
    message_dict = updated_message.dict(exclude_unset=True)
    message_dict["edit_timestamp"] = time.time()
    result = await messages_collection.update_one({"_id": ObjectId(id)}, {"$set": message_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    updated_message = await messages_collection.find_one({"_id": ObjectId(id)})
    return {"id": str(updated_message["_id"])}

@router.delete("/messages/{id}")
async def delete_message(id: str):
    result = await messages_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"id": id}





@router.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            random_message = await messages_collection.aggregate([
                {"$sample": {"size": 1}} 
            ]).to_list(1)
            
            if random_message:
                message_content = random_message[0]['content']
                await websocket.send_text(message_content)
            
            await asyncio.sleep(1) 
    except WebSocketDisconnect:
        print("User disconnected")
