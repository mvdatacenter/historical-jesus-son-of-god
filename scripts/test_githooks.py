"""Tests for the tracked .githooks wrappers and the ignore rules they depend on."""

from __future__ import annotations

import os
import pathlib
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOKS = REPO_ROOT / ".githooks"
CENTRAL = "https://raw.githubusercontent.com/mvdatacenter/ai-instructions/main/hooks"
WRAPPERS = ("pre-commit", "post-checkout")

# -f makes curl exit non-zero on a 404, and the -o path it has already created
# stays behind holding whatever arrived.
CURL_STUB = """\
#!/bin/sh
out=""
while [ $# -gt 0 ]; do
    if [ "$1" = "-o" ]; then out="$2"; fi
    shift
done
[ -n "$out" ] && printf '<html>404</html>' > "$out"
exit 22
"""


def wrapper_source(name: str) -> str:
    return (HOOKS / name).read_text()


def run_against_a_404(hook: str, workdir: pathlib.Path) -> subprocess.CompletedProcess:
    stub_bin = workdir / "bin"
    stub_bin.mkdir()
    (stub_bin / "curl").write_text(CURL_STUB)
    (stub_bin / "gh").write_text("#!/bin/sh\nexit 1\n")
    (stub_bin / "curl").chmod(0o755)
    (stub_bin / "gh").chmod(0o755)

    return subprocess.run(
        ["bash", str(HOOKS / hook)],
        cwd=workdir,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{stub_bin}{os.pathsep}{os.environ['PATH']}"},
    )


def ignored_by_the_tracked_rules(candidate: str, workdir: pathlib.Path) -> bool:
    repo = workdir / "throwaway"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / ".gitignore").write_text((REPO_ROOT / ".gitignore").read_text())

    result = subprocess.run(
        ["git", "-c", "core.excludesFile=/dev/null", "-C", str(repo),
         "check-ignore", "--quiet", candidate],
        capture_output=True,
        text=True,
    )
    assert result.returncode in (0, 1), f"check-ignore errored on {candidate}: {result.stderr}"

    return result.returncode == 0


@pytest.mark.parametrize("name", WRAPPERS)
def test_wrapper_fetches_from_ai_instructions(name: str) -> None:
    source = wrapper_source(name)

    assert f'RAW="{CENTRAL}/{name}.sh"' in source
    assert "claude-instructions" not in source


@pytest.mark.parametrize("name", WRAPPERS)
def test_wrapper_caches_under_ai_shared(name: str) -> None:
    source = wrapper_source(name)

    assert f'SCRIPT=".ai-shared/{name}.sh"' in source
    assert ".claude-shared" not in source


def test_pre_commit_refuses_the_commit_it_could_not_check(tmp_path) -> None:
    result = run_against_a_404("pre-commit", tmp_path)

    assert result.returncode == 1, "a commit whose central checks never ran was allowed through"
    assert ".ai-shared/pre-commit.sh is missing and could not be fetched" in result.stderr
    assert f"{CENTRAL}/pre-commit.sh" in result.stderr


def test_pre_commit_leaves_no_partial_download_as_the_cache(tmp_path) -> None:
    run_against_a_404("pre-commit", tmp_path)

    leftovers = sorted(p.name for p in (tmp_path / ".ai-shared").iterdir())
    assert leftovers == [], "a half-written fetch became the cache every later commit would run"


def test_gitignore_ignores_the_cache_the_wrappers_write(tmp_path) -> None:
    assert ignored_by_the_tracked_rules(".ai-shared/pre-commit.sh", tmp_path)


def test_gitignore_still_ignores_the_pre_rename_cache(tmp_path) -> None:
    assert ignored_by_the_tracked_rules(".claude-shared/post-checkout.sh", tmp_path)


def test_gitignore_leaves_every_tracked_hook_addable(tmp_path) -> None:
    for entry in sorted(HOOKS.iterdir()):
        hook = f".githooks/{entry.name}"
        workdir = tmp_path / entry.name
        workdir.mkdir()

        assert not ignored_by_the_tracked_rules(hook, workdir), (
            f"{hook} is ignored, so git add refuses a file this repository tracks"
        )
