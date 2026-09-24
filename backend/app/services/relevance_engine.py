def calculate_relevance_score(
    downloads: int,
    dependents: int,
    package_age_days: int,
    release_count: int
):
    """
    Calculate the relevance score of an npm package.

    Score range: 0 - 100
    """

    score = 0

    # -------------------------
    # 1. Download Signal (0-40)
    # -------------------------
    if downloads >= 100_000_000:
        score += 40
    elif downloads >= 10_000_000:
        score += 35
    elif downloads >= 1_000_000:
        score += 30
    elif downloads >= 100_000:
        score += 20
    elif downloads >= 10_000:
        score += 10
    else:
        score += 5

    # -------------------------
    # 2. Dependent Signal (0-25)
    # -------------------------
    if dependents >= 10_000:
        score += 25
    elif dependents >= 1_000:
        score += 20
    elif dependents >= 100:
        score += 15
    elif dependents >= 10:
        score += 10
    else:
        score += 5

    # -------------------------
    # 3. Package Age (0-15)
    # -------------------------
    if package_age_days >= 365 * 5:
        score += 15
    elif package_age_days >= 365 * 2:
        score += 12
    elif package_age_days >= 365:
        score += 10
    elif package_age_days >= 180:
        score += 7
    else:
        score += 4

    # -------------------------
    # 4. Release Activity (0-20)
    # -------------------------
    if release_count >= 100:
        score += 20
    elif release_count >= 50:
        score += 15
    elif release_count >= 20:
        score += 10
    elif release_count >= 5:
        score += 7
    else:
        score += 3

    # Make sure score stays within 0-100
    score = min(score, 100)

    # -------------------------
    # Priority
    # -------------------------
    if score >= 70:
        priority = "HIGH"
    elif score >= 40:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return score, priority
