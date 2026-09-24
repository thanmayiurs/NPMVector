from app.services.relevance_service import calculate_package_relevance

packages = [
    "express",
    "react",
    "lodash",
    "axios",
    "fastapi"
]

for package in packages:

    calculate_package_relevance(package)
