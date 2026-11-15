
def prepare_nic_research(activity_descriptions):
    if not isinstance(activity_descriptions, list):
        activity_descriptions = []

    activities = [
        item.strip()
        for item in activity_descriptions
        if isinstance(item, str) and item.strip()
    ]

    combined = " ".join(activities).lower()

    candidates = []

    if any(word in combined for word in [
        "repair", "maintenance", "servicing", "car modification",
        "vehicle modification", "vehicle accessories"
    ]):
        candidates.append({
            "nic_code": "45200",
            "description": "Maintenance and repair of motor vehicles",
            "reason": (
                "Covers motor vehicle maintenance, repair and "
                "installation of parts and accessories not as "
                "part of the manufacturing process."
            ),
            "source": (
                "https://www.udyamregistration.gov.in/docs/"
                "NIC-code-for-MSME-classification-definition.pdf"
            )
        })

    if any(word in combined for word in [
        "sale of car parts", "sale of vehicle parts",
        "retail sale of accessories", "vehicle spare parts"
    ]):
        candidates.append({
            "nic_code": "45300",
            "description": "Sale of motor vehicle parts and accessories",
            "reason": "Potential match for a separate parts/accessories sales activity.",
            "source": (
                "https://www.udyamregistration.gov.in/docs/"
                "NIC-code-for-MSME-classification-definition.pdf"
            )
        })

    return {
        "activities_received": activities,
        "candidate_codes": candidates,
        "manual_verification_required": True,
        "note": (
            "These are suggested candidates, not an automatic final "
            "classification. Confirm the actual business activities "
            "and the code available on the Udyam portal."
        )
    }
