def calculate_threat_score(
    has_install_script=False,
    has_new_dependency=False,
    dependency_count_increased=False,
    unusual_release=False,
    maintainer_changed=False,
    package_size_increased=False
):
    """Calculate an explainable threat score for an npm release.

    Score range: 0 - 100
    """

    score = 0
    flags = []

    if has_install_script:
        score += 25
        flags.append("install_script")

    if has_new_dependency:
        score += 15
        flags.append("new_dependency")

    if dependency_count_increased:
        score += 10
        flags.append("dependency_count_increased")

    if unusual_release:
        score += 20
        flags.append("unusual_release")

    if maintainer_changed:
        score += 20
        flags.append("maintainer_changed")

    if package_size_increased:
        score += 10
        flags.append("package_size_increased")

    score = min(score, 100)

    return score, flags


def get_threat_level(score):
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"