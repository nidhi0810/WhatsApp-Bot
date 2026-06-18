def build_filters(user):
    filters = []

    # Value filters

    if user.get("gender"):
        filters.append({
            "identifier": "gender",
            "value": user["gender"]
        })

    if user.get("state"):
        filters.append({
            "identifier": "beneficiaryState",
            "value": user["state"]
        })

    if user.get("caste"):
        filters.append({
            "identifier": "caste",
            "value": user["caste"]
        })

    if user.get("occupation"):
        filters.append({
            "identifier": "occupation",
            "value": user["occupation"]
        })

    if user.get("employmentStatus"):
        filters.append({
            "identifier": "employmentStatus",
            "value": user["employmentStatus"]
        })

    if user.get("residence"):
        filters.append({
            "identifier": "residence",
            "value": user["residence"]
        })

    if user.get("schemeCategory"):
        filters.append({
            "identifier": "schemeCategory",
            "value": user["schemeCategory"]
        })

    if user.get("benefitTypes"):
        filters.append({
            "identifier": "benefitTypes",
            "value": user["benefitTypes"]
        })

    if user.get("maritalStatus"):
        filters.append({
            "identifier": "maritalStatus",
            "value": user["maritalStatus"]
        })

    # Boolean filters

    if user.get("isStudent"):
        filters.append({
            "identifier": "isStudent",
            "value": "Yes"
        })

    if user.get("minority"):
        filters.append({
            "identifier": "minority",
            "value": "Yes"
        })

    if user.get("isBpl"):
        filters.append({
            "identifier": "isBpl",
            "value": "Yes"
        })

    if user.get("dbtScheme"):
        filters.append({
            "identifier": "dbtScheme",
            "value": "Yes"
        })

    if user.get("isGovEmployee"):
        filters.append({
            "identifier": "isGovEmployee",
            "value": "Yes"
        })

    if user.get("disability"):
        filters.append({
            "identifier": "disability",
            "value": "Yes"
        })

    if user.get("isEconomicDistress"):
        filters.append({
            "identifier": "isEconomicDistress",
            "value": "Yes"
        })

    # Age bucket

    age = user.get("age")

    if age is not None:

        age_ranges = [
            (0, 10),
            (11, 20),
            (21, 30),
            (31, 40),
            (41, 50),
            (51, 60),
            (61, 70),
            (71, 80),
            (81, 120)
        ]

        for mn, mx in age_ranges:
            if mn <= age <= mx:
                filters.append({
                    "identifier": "age-general",
                    "min": mn,
                    "max": mx
                })
                break

    # Disability percentage

    if user.get("disabilityPercentage") is not None:
        filters.append({
            "identifier": "disabilityPercentage",
            "min": user["disabilityPercentage"],
            "max": user["disabilityPercentage"]
        })

    return filters