from db import users

def get_user(user_id, name=None):

    user = users.find_one({
        "userId": user_id
    })

    if not user:

        user = {
            "userId": user_id,
            "name": name,

            # Basic
            "age": None,
            "gender": None,
            "city": None,
            "state": None,
            "income": None,

            # Education / Occupation
            "occupation": None,
            "isStudent": None,
            "employmentStatus": None,

            # Social
            "caste": None,
            "minority": None,

            # Residence
            "residence": None,

            # Family
            "maritalStatus": None,

            # Financial
            "isBpl": None,

            # Government / Special Categories
            "isGovEmployee": None,
            "disability": None,
            "disabilityPercentage": None,
            "isEconomicDistress": None,

            # Preferences
            "schemeCategory": None,
            "benefitTypes": None
        }

        users.insert_one(user)

        return user

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