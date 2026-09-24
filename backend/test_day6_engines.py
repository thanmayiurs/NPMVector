from app.services.package_analyzer import (
    analyze_package_json,
    compare_dependencies,
)
from app.services.monitor_service import is_new_release
from app.services.relevance_engine import calculate_relevance_score
from app.services.security_engine import calculate_threat_score, get_threat_level


def test_release_detection_with_controlled_versions():
    assert is_new_release("5.2.0", "5.2.1") is True
    assert is_new_release("5.2.1", "5.2.1") is False
    assert is_new_release(None, "5.2.1") is True


def test_relevance_score_boundaries():
    high_score, high_priority = calculate_relevance_score(100_000_000, 10_000, 2000, 100)
    low_score, low_priority = calculate_relevance_score(500, 0, 30, 1)
    medium_score, medium_priority = calculate_relevance_score(100_000, 100, 365, 20)

    assert high_score == 100 and high_priority == "HIGH"
    assert low_score == 17 and low_priority == "LOW"
    assert medium_score == 55 and medium_priority == "MEDIUM"


def test_security_engine_signals_and_levels():
    install_score, install_flags = calculate_threat_score(has_install_script=True)
    combined_score, combined_flags = calculate_threat_score(
        has_new_dependency=True,
        unusual_release=True,
    )
    clean_score, clean_flags = calculate_threat_score()

    assert (install_score, install_flags) == (25, ["install_script"])
    assert (combined_score, combined_flags) == (35, ["new_dependency", "unusual_release"])
    assert (clean_score, clean_flags) == (0, [])
    assert get_threat_level(25) == "LOW"
    assert get_threat_level(50) == "MEDIUM"
    assert get_threat_level(75) == "HIGH"


def test_package_analyzer_comparison():
    package_data = {
        "dist-tags": {"latest": "5.2.1"},
        "versions": {
            "5.2.1": {
                "scripts": {"postinstall": "node setup.js"},
                "dependencies": {"new-package": "^1.0.0"},
            }
        },
    }

    assert analyze_package_json(package_data)[0]["type"] == "install_script"
    assert compare_dependencies({}, {"new-package": "^1.0.0"}) == {
        "added": ["new-package"],
        "removed": [],
        "changed": [],
    }
