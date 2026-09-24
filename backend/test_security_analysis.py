from app.services.npm_monitor import get_package
from app.services.package_analyzer import (
    analyze_package_json,
    get_dependencies,
)


package_name = "express"
data = get_package(package_name)
flags = analyze_package_json(data)
dependencies = get_dependencies(data)

print("Security Flags:")
for flag in flags:
    print(flag)

print("Dependency count:", len(dependencies))