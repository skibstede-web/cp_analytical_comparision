from pathlib import Path


REQUIRED_DOCUMENTATION_FILES = [
    "README.md",
    "docs/CODING_AGENT_INSTRUCTIONS.md",
    "docs/STATISTICAL_DECISION_RULES.md",
    "docs/USP1010_TRACEABILITY_MATRIX.md",
    "docs/CP_METHOD_MODULES.md",
    "docs/PDF_EXPORT_WORKFLOW.md",
    "docs/REVIEW_CHECKLIST.md",
    "docs/REGULATORY_RESOURCE_HANDLING.md",
    "docs/DECISION_LOG.md",
]


def test_required_documentation_files_exist() -> None:
    for file_path in REQUIRED_DOCUMENTATION_FILES:
        assert Path(file_path).is_file(), f"Missing documentation file: {file_path}"


def test_readme_contains_core_commands_and_private_resource_policy() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "uv sync" in readme
    assert "uv run pytest" in readme
    assert "resources/private" in readme
