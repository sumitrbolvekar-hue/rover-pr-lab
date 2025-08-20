"""Ground truth about the student's repository. Read-only: never changes the repo and never uses the network."""
from __future__ import annotations

import os
import re
import subprocess
from typing import List, NamedTuple, Optional, Set, Tuple

STAFF_SUBJECT = "chore: add lab assignment and grader"
COURSE_SLUG = "qbit-glitch/26ra2308-gitlab-11-rover-pr-lab"  # lower case; the course repository students start from
REPO_NAME = "rover-pr-lab"
USAGE_SUBJECT = "docs: add usage instructions to readme"
FIXLINK_SUBJECT = "docs: fix broken link in usage section"
DETECTOR_SUBJECT = "fix(vision): raise the detection threshold"
CREEP_SUBJECT = "feat(control): add creep speed"
CREEP_DOC_SUBJECT = "docs: document the creep speed"
CONTRIB_SUBJECT = "docs: add contributing guide"
README_BASE = ("# Kestrel-1 rover\n\nControl and vision code for the Kestrel-1 rover.\n\n"
               "See [the installation notes](docs/install.md) to set up a laptop.\n")
USAGE_GOOD = ("\n## Usage\n\nInstall the requirements first (see [the install guide](docs/install.md)), then run:\n\n"
              "    python3 src/controller.py\n")
README_FIXED = README_BASE + USAGE_GOOD
CONTRIBUTING = """# Contributing to Kestrel-1

## Branching strategy
- Branch from `main` for every feature or fix.
- Name branches `feature/<short-description>` or `fix/<short-description>`.

## Commit messages
Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`.

## Pull requests
- All changes must go through a pull request.
- At least one reviewer approval is required before merging.
- Link pull requests to issues with `Closes #<number>`.
"""
GIT_TIMEOUT = 60
SLUG_RE = re.compile(r"github\.com[:/]([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:/|\s|$)")


class GitError(RuntimeError):
    """Raised when the repository is not set up the way the grader expects."""


class Commit(NamedTuple):
    """A commit with the facts the grader needs."""

    sha: str
    author: str
    email: str
    committer_email: str
    subject: str
    parents: List[str]


FORMAT = "--format=%H%x1f%an%x1f%ae%x1f%ce%x1f%s%x1f%P"


def _commit(line: str) -> Optional[Commit]:
    parts = line.rstrip("\n").split("\x1f")
    return Commit(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5].split()) if len(parts) == 6 else None


def slug_of(url: str) -> str:
    """'owner/repo' (lower case) of a GitHub address in any of its forms ('' if it is not a GitHub address)."""
    match = SLUG_RE.search(url.strip() + " ")
    return f"{match.group(1)}/{match.group(2)}".lower() if match else ""


def run_git_rc(repo: str, *args: str) -> Tuple[int, str]:
    """Run git in 'repo' and return (exit code, stdout); a git call that hangs is stopped and reported as 124."""
    env = dict(os.environ, LC_ALL="C", GIT_PAGER="cat", GIT_TERMINAL_PROMPT="0")
    try:
        proc = subprocess.run(["git", *args], cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              encoding="utf-8", errors="replace", timeout=GIT_TIMEOUT)
    except (subprocess.TimeoutExpired, OSError):
        return 124, ""
    return proc.returncode, proc.stdout


def run_git(repo: str, *args: str) -> str:
    """Run git in 'repo' and return stdout ('' on failure)."""
    return run_git_rc(repo, *args)[1]


class Facts:
    """Everything the grader needs to know about the repository."""

    def __init__(self, repo: str) -> None:
        self.repo = os.path.abspath(repo)
        if run_git_rc(self.repo, "rev-parse", "--verify", "-q", "refs/heads/main^{commit}")[0] != 0:
            raise GitError("branch main not found. Run the grader inside your clone of the lab repository.")
        log = [c for c in map(_commit, run_git(self.repo, "log", "refs/heads/main", FORMAT).splitlines()) if c]
        staff = [c for c in log if c.subject == STAFF_SUBJECT]
        if not staff:
            raise GitError(f"the starting commit '{STAFF_SUBJECT}' is not in the history of main. "
                           "Run the grader inside your clone of the lab repository (made with 'git clone').")
        self.base: str = staff[-1].sha
        self.published: List[Commit] = [c for c in map(_commit, run_git(self.repo, "log", self.base, FORMAT).splitlines()) if c]

    def published_emails(self) -> Set[str]:
        """E-mail addresses of the people who wrote the starting history."""
        return {c.email.lower() for c in self.published}

    def published_names(self) -> Set[str]:
        """Names of the people who wrote the starting history."""
        return {c.author.lower() for c in self.published}

    def config_value(self, key: str) -> str:
        """Value of a repository-local config key ('' if unset)."""
        return run_git(self.repo, "config", "--local", "--get", key).strip()

    def effective_config(self, key: str) -> str:
        """Value of a config key as Git uses it here, local or global ('' if unset)."""
        return run_git(self.repo, "config", "--get", key).strip()

    def remote_url(self, name: str) -> str:
        """The address stored for remote 'name' ('' if there is none)."""
        return self.config_value(f"remote.{name}.url")

    def branch_config(self, branch: str) -> Tuple[str, str]:
        """(remote, merge ref) a local branch is set up to track ('' for unset values)."""
        return self.config_value(f"branch.{branch}.remote"), self.config_value(f"branch.{branch}.merge")

    def rev(self, ref: str) -> str:
        """Full SHA of 'ref' ('' if it does not name a commit)."""
        return run_git(self.repo, "rev-parse", "--verify", "-q", f"{ref}^{{commit}}").strip()

    def commit_exists(self, token: str) -> bool:
        """True if 'token' names a commit object in this repository."""
        return bool(token) and run_git_rc(self.repo, "cat-file", "-e", f"{token}^{{commit}}")[0] == 0

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        """True if commit 'ancestor' is 'descendant' itself or part of its history."""
        return bool(ancestor) and bool(descendant) \
            and run_git_rc(self.repo, "merge-base", "--is-ancestor", ancestor, descendant)[0] == 0

    def file_at(self, ref: str, path: str) -> Optional[str]:
        """Content of 'path' at 'ref' (None if absent)."""
        code, out = run_git_rc(self.repo, "show", f"{ref}:{path}")
        return out if code == 0 else None

    def commit(self, ref: str) -> Optional[Commit]:
        """The commit 'ref' names (None if it names nothing)."""
        sha = self.rev(ref)
        return _commit(run_git(self.repo, "show", "-s", FORMAT, sha)) if sha else None

    def above_base(self) -> List[Commit]:
        """Every commit of main that is not part of the starting history, oldest first."""
        out = run_git(self.repo, "log", "--reverse", FORMAT, f"{self.base}..refs/heads/main")
        return [c for c in map(_commit, out.splitlines()) if c]

    def with_subject(self, subject: str, prefix: bool = False) -> Optional[Commit]:
        """The newest commit above the starting commit with this subject (or starting with it)."""
        for commit in reversed(self.above_base()):
            if commit.subject == subject or (prefix and commit.subject.startswith(subject)):
                return commit
        return None

    def main_tip(self) -> str:
        """Full SHA of the local branch main."""
        return self.rev("refs/heads/main")

    def local_branch(self, name: str) -> str:
        """SHA of a local branch ('' if there is none)."""
        return self.rev(f"refs/heads/{name}")

    def reflog(self, ref: str) -> List[str]:
        """Reflog messages of 'ref', newest first (empty if there is no reflog)."""
        return run_git(self.repo, "log", "-g", "--format=%gs", ref, "--").splitlines()

    def working_tree_clean(self) -> bool:
        """True when 'git status --porcelain' prints nothing and no merge or rebase is in progress."""
        clean = run_git(self.repo, "status", "--porcelain").strip() == ""
        merging = run_git_rc(self.repo, "rev-parse", "-q", "--verify", "MERGE_HEAD")[0] == 0
        return clean and not merging
