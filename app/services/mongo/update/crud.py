from app.db.mongodb import get_db
from app.models.BaseModel.mongo.Schema import Response, User
async def update_response(response_id: str, response_data: Response) -> Response:
    """
    Update a response in the MongoDB database.
    """
    db = get_db()
    response_dict = response_data.model_dump(by_alias=True)
    result = await db.responses.update_one({"_id": response_id}, {"$set": response_dict})
    
    if result.modified_count == 0:
        raise ValueError("No response found with the given ID.")
    
    return response_data

async def update_user(user_id: str, user_data: User) -> User:
    """
    Update a user in the MongoDB database.
    """
    db = get_db()
    user_dict = user_data.model_dump(by_alias=True)
    result = await db.users.update_one({"_id": user_id}, {"$set": user_dict})
    
    if result.modified_count == 0:
        raise ValueError("No user found with the given ID.")
    
    return user_data