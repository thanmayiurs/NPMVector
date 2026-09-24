from datetime import datetime

import requests

NPM_REGISTRY_URL = "https://registry.npmjs.org"


def parse_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return None


def get_package(package_name: str):
    url = f"{NPM_REGISTRY_URL}/{package_name}"

    response = requests.get(
        url,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def get_latest_version(package_data: dict):
    return package_data.get("dist-tags", {}).get("latest")


def get_package_metadata(package_data: dict):
    latest_version = get_latest_version(package_data)

    return {
        "name": package_data.get("name"),
        "description": package_data.get("description"),
        "latest_version": latest_version,
        "created_at": package_data.get("time", {}).get("created"),
        "modified_at": package_data.get("time", {}).get("modified"),
    }


def get_downloads(package_name: str):

    url = (
        "https://api.npmjs.org/downloads/point/"
        f"last-week/{package_name}"
    )

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return data.get("downloads", 0)
