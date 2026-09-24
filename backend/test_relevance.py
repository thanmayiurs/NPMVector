from app.services.relevance_engine import calculate_relevance_score

score, priority = calculate_relevance_score(
    downloads=97_784_379,
    dependents=1000,
    package_age_days=2000,
    release_count=100
)

print("Relevance Score:", score)
print("Priority:", priority)
