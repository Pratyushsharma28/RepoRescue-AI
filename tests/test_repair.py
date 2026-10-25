from pathlib import Path
from core.investigator import investigate
from core.repairer import propose_patch, apply_patch


def test_investigator_finds_bug(tmp_path):
    (tmp_path / "calculator.py").write_text(
        "def calculate_total(price, quantity):\n"
        "    return price + quantity\n"
    )

    result = investigate(str(tmp_path))
    assert result["ok"] is True


def test_repair_requires_approval(tmp_path):
    source = tmp_path / "calculator.py"
    source.write_text(
        "def calculate_total(price, quantity):\n"
        "    return price + quantity\n"
    )

    patch = propose_patch(str(tmp_path))
    result = apply_patch(patch, approval=False)

    assert result["ok"] is False
    assert "+" in source.read_text()


def test_repair_proposes_correct_expression(tmp_path):
    (tmp_path / "calculator.py").write_text(
        "def calculate_total(price, quantity):\n"
        "    return price + quantity\n"
    )

    patch = propose_patch(str(tmp_path))

    assert patch["ok"] is True
    assert "return price * quantity" in patch["updated"]