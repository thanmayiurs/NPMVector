from app.services.npm_monitor import get_package, get_package_metadata

package_name = "express"

data = get_package(package_name)
metadata = get_package_metadata(data)

print("Package:", metadata["name"])
print("Description:", metadata["description"])
print("Latest Version:", metadata["latest_version"])
print("Created:", metadata["created_at"])
print("Modified:", metadata["modified_at"])
