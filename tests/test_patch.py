# pylint: disable=missing-function-docstring
"""
test for patch cli
"""


from shutil import copy

import pytest
from properties_tools.patch import run

from . import SAMPLE1, SAMPLE1_ALT, SAMPLE2, execute

NOT_QUIET = 2
ADDED = 1
DELETED = 1
MODIFIED = 2


def test_bad_sep(capsys):
    with pytest.raises(SystemExit):
        execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE1} --add --sep /")
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 0
    assert len(captured.err.splitlines()) == 2


def test_samefile(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE1} --add")
    assert len(out) == 7
    assert len(err) == 0
    assert "database.type=postgresql" in out
    assert "database.type=mysql" not in out


def test_altfile(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE1_ALT} --add")
    assert len(out) == 7
    assert len(err) == 0
    assert "database.type=postgresql" in out
    assert "database.type=mysql" not in out


def test_update(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -U")
    assert len(out) == 7
    assert len(err) == 0
    assert "database.type=postgresql" not in out
    assert "database.type=mysql" in out
    assert "database.version=12" not in out
    assert "database.host=localhost" in out


def test_add(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -A")
    assert len(out) == 8
    assert len(err) == 0
    assert "database.type=postgresql" in out
    assert "database.type=mysql" not in out
    assert "database.version=12" in out
    assert "database.host=localhost" in out


def test_delete(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -D")
    assert len(out) == 6
    assert len(err) == 0
    assert "database.type=postgresql" in out
    assert "database.type=mysql" not in out
    assert "database.version=12" not in out
    assert "database.host=localhost" not in out


def test_adu(capsys):
    out, err = execute(run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -ADU")
    assert len(out) == 7
    assert len(err) == 0
    assert "database.type=postgresql" not in out
    assert "database.type=mysql" in out
    assert "database.version=12" in out
    assert "database.host=localhost" not in out


def test_output(capsys, tmp_path):
    output = tmp_path / "output.properties"
    out, err = execute(
        run, capsys, f"{SAMPLE1}  --patch {SAMPLE2} -ADU --output {output} --comments"
    )
    assert len(out) == 11
    assert len(err) == 0
    assert "database.type=postgresql" not in out
    assert "database.type=mysql" in out
    assert "database.version=12" in out
    assert "database.host=localhost" not in out
    assert output.exists()
    assert output.read_text().splitlines() == out


def test_no_overwrite(capsys, tmp_path):
    source = tmp_path / "source.properties"
    patch = tmp_path / "patch.properties"
    output = tmp_path / "output.properties"

    copy(SAMPLE1, source)
    copy(SAMPLE2, patch)

    output = tmp_path / "output.properties"
    execute(run, capsys, f"{source}  --patch {patch} -ADU --output {output} --comments")
    assert output.exists()

    with pytest.raises(SystemExit):
        execute(
            run, capsys, f"{source}  --patch {patch} -ADU --output {output} --comments"
        )


def test_in_place(capsys, tmp_path):
    source = tmp_path / "source.properties"
    patch = tmp_path / "patch.properties"

    copy(SAMPLE1, source)
    copy(SAMPLE2, patch)

    source_text = source.read_text()
    execute(run, capsys, f"{source}  --patch {patch} -ADU --overwrite --comments")
    assert source_text != source.read_text()
