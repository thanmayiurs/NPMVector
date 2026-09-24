def analyze_package_json(package_data: dict):
    flags = []

    latest_version = package_data.get("dist-tags", {}).get("latest")
    if not latest_version:
        return flags

    version_data = package_data.get("versions", {}).get(latest_version, {})
    scripts = version_data.get("scripts", {})
    dangerous_scripts = ["preinstall", "install", "postinstall"]

    for script in dangerous_scripts:
        if script in scripts:
            flags.append({
                "type": "install_script",
                "script": script,
                "value": scripts[script]
            })

    return flags


def get_dependencies(package_data: dict):
    latest_version = package_data.get("dist-tags", {}).get("latest")
    version_data = package_data.get("versions", {}).get(latest_version, {})
    return version_data.get("dependencies", {})


def compare_dependencies(previous_dependencies, current_dependencies):
    previous_dependencies = previous_dependencies or {}
    current_dependencies = current_dependencies or {}

    added = []
    removed = []
    changed = []

    for package, version in current_dependencies.items():
        if package not in previous_dependencies:
            added.append(package)
        elif previous_dependencies[package] != version:
            changed.append({
                "package": package,
                "from": previous_dependencies[package],
                "to": version
            })

    for package in previous_dependencies:
        if package not in current_dependencies:
            removed.append(package)

    return {
        "added": added,
        "removed": removed,
        "changed": changed
    }