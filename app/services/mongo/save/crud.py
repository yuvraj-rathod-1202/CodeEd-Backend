from app.db.mongodb import get_db
from app.models.BaseModel.mongo.Schema import Response, User

async def save_response(response: Response) -> Response:
    """
    Save a response to the MongoDB database.
    """
    db = get_db()
    response_dict = response.model_dump(by_alias=True)
    response_dict.pop("_id", None)
    result = await db.responses.insert_one(response_dict)
    response._id = result.inserted_id
    return response

async def save_user(user_data: User) -> User:
    """
    Save a user to the MongoDB database.
    """
    db = get_db()
    user_dict = user_data.model_dump(by_alias=True)
    user_dict.pop("_id", None)
    result = await db.users.insert_one(user_dict)
    user_data._id = result.inserted_id
    return user_data