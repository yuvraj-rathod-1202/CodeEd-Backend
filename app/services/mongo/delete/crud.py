from app.db.mongodb import get_db
from app.models.BaseModel.mongo.Schema import Response, User
async def delete_response(response_id: str) -> bool:
    """
    Delete a response from the MongoDB database.
    """
    db = get_db()
    result = await db.responses.delete_one({"_id": response_id})
    
    if result.deleted_count == 0:
        raise ValueError("No response found with the given ID.")
    
    return True

async def delete_user(user_id: str) -> bool:
    """
    Delete a user from the MongoDB database.
    """
    db = get_db()
    result = await db.users.delete_one({"_id": user_id})
    
    if result.deleted_count == 0:
        raise ValueError("No user found with the given ID.")
    
    return True

