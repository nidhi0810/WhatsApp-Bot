from db import users

def get_user(user_id, name=None):

    user = users.find_one({
        "userId": user_id
    })

    if not user:

        user = {
            "userId": user_id,
            "name": name,
            "age": None,
            "occupation": None,
            "income": None,
            "city": None
        }

        users.insert_one(user)

        return user

    # update name if we got a better one
    if (
        name
        and name != "Unknown"
        and user.get("name") != name
    ):

        users.update_one(
            {"userId": user_id},
            {
                "$set": {
                    "name": name
                }
            }
        )

        user["name"] = name

    return user
    
def update_user(user_id, updates):

    users.update_one(
        {"userId": user_id},
        {
            "$set": updates
        }
    )

    return users.find_one({
        "userId": user_id
    })