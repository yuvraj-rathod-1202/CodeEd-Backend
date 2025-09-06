# from app.models.BaseModel.mongo.Schema import User, UserResponse
# from app.services.mongo.save.crud import save_user

# async def save_user_data_logic(request: User) -> UserResponse:
#     """
#     Logic to save user data.

#     Args:
#         request (User): The user data to be saved.

#     Returns:
#         UserResponse: The response containing the saved user data.
#     """
#     # Assuming we have a function to save the user data in the database
#     saved_user = await save_user(request)

#     # Return the saved user data as a response
#     return UserResponse(user_id=saved_user._id)