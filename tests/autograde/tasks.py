"""Graders for the five tasks of the Pull Request lab."""
from __future__ import annotations

import re
from typing import List, Optional

from .context import Ctx
from .facts import (
    COURSE_SLUG, CONTRIBUTING, CONTRIB_SUBJECT, CREEP_DOC_SUBJECT, CREEP_SUBJECT, DETECTOR_SUBJECT, FIXLINK_SUBJECT, README_FIXED,
    REPO_NAME, USAGE_SUBJECT, slug_of,
)
from .framework import Task
from .textutil import get_answer, oneline_entries, strip_decoration

PLACEHOLDER_NAMES = {"", "your full name", "your name"}
PLACEHOLDER_EMAILS = {"", "your.email@example.com", "your-email@example.com"}
TO_LINE_RE = re.compile(r"(?m)^To (\S+)\s*$")
COMMIT_LINE_RE = r"(?m)^\[(\S+) (?:\(root-commit\) )?([0-9a-f]{7,40})\] (.*)$"
RANGE_RE = r"(?m)^\s+([0-9a-f]{7,40})\.\.([0-9a-f]{7,40})\s+(\S+)\s+->\s+(\S+)\s*$"
URL_RE = r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/(issues|pull)/(\d+)"
KEYWORDS = {"close", "closes", "closed", "fix", "fixes", "fixed", "resolve", "resolves", "resolved"}


def clean(text: str) -> str:
    """The pasted text without the '$ command' lines a student may have copied along with the output."""
    return "\n".join(ln for ln in text.split("\n") if not ln.startswith("$ "))


def own_slug(ctx: Ctx) -> str:
    """'owner/repo' of the student's own repository: from the clone's config when it can be read, else from the pasted 1.1."""
    live = slug_of(ctx.facts.remote_url("origin")) if ctx.repo_mode else ""
    if live and live != COURSE_SLUG:
        return live
    match = TO_LINE_RE.search(clean(ctx.step("1.1")))
    return slug_of(match.group(1)) if match else ""


def to_slug(text: str) -> str:
    """'owner/repo' named by the first 'To <address>' line of a pasted push ('' if there is none)."""
    match = TO_LINE_RE.search(clean(text))
    return slug_of(match.group(1)) if match else ""


def url_for(ctx: Ctx, text: str, kind: str) -> Optional[int]:
    """The number in the first github.com/<own>/issues|pull/<n> address of a pasted output ('kind' is issues or pull)."""
    for match in re.finditer(URL_RE, clean(text)):
        if match.group(3) == kind and f"{match.group(1)}/{match.group(2)}".lower() == own_slug(ctx):
            return int(match.group(4))
    return None


def _answer(ctx: Ctx, number: int) -> str:
    return get_answer(ctx.text, number).strip("`'\" ").strip()


def _printed(text: str, pattern: str = COMMIT_LINE_RE) -> Optional["re.Match[str]"]:
    return re.search(pattern, clean(text))


def pr_number(ctx: Ctx) -> Optional[int]:
    """The number of the first pull request (from the address 2.3 printed)."""
    return url_for(ctx, ctx.step("2.3"), "pull")


def _merged(ctx: Ctx, step: str, word: str, title: str) -> Optional[int]:
    """The pull request number in 'gh pr merge' output like '✓ Squashed and merged pull request owner/repo#3 (title)'."""
    match = re.search(rf"(?m)^\W*{word} pull request (?:\S*)?#(\d+) \({re.escape(title)}\)\s*$", clean(ctx.step(step)))
    return int(match.group(1)) if match else None


def own_identity(ctx: Ctx) -> bool:
    """True when the identity Git uses here is the student's own (not a placeholder, not a teammate's)."""
    f = ctx.facts
    name, email = f.effective_config("user.name"), f.effective_config("user.email")
    return name.lower() not in PLACEHOLDER_NAMES and "@" in email and email.lower() not in PLACEHOLDER_EMAILS \
        and name.lower() not in f.published_names() and email.lower() not in f.published_emails()


# -- Task 1 -----------------------------------------------------------------
def grade_task1(ctx: Ctx) -> Task:
    """Task 1: connect the clone to your own GitHub repository, then plan the work with two issues."""
    t = Task(1, "Connect and plan the work", 20, ctx.repo_mode)
    f = ctx.facts
    mine = own_slug(ctx)
    s11, s12, s15 = clean(ctx.step("1.1")), clean(ctx.step("1.2")), clean(ctx.step("1.5"))
    t.check(2, "1.1 push output: '* [new branch]  main -> main'", lambda: re.search(r"\* \[new branch\]\s+main -> main", s11) is not None)
    t.check(1, "1.1 push output: branch 'main' set up to track 'origin/main'",
            lambda: re.search(r"(?i)branch 'main' set up to track (?:remote branch 'main' from 'origin'|'origin/main')", s11) is not None)
    t.check(1, "1.1 the push went to your own GitHub repository (not the course repository)",
            lambda: bool(to_slug(s11)) and to_slug(s11) != COURSE_SLUG and to_slug(s11) == mine)
    t.check(2, "1.2 gh auth status: 'Logged in to github.com account <you>', the owner of your repository",
            lambda: re.search(r"Logged in to github\.com account (\S+)", s12) is not None
            and re.search(r"Logged in to github\.com account (\S+)", s12).group(1).lower() == mine.split("/")[0])  # type: ignore[union-attr]
    t.check(3, "1.3 the address of issue 1 in your own repository (https://github.com/<you>/rover-pr-lab/issues/1)",
            lambda: url_for(ctx, ctx.step("1.3"), "issues") == 1)
    t.check(3, "1.4 the address of issue 2 in your own repository",
            lambda: url_for(ctx, ctx.step("1.4"), "issues") == 2)
    t.check(3, "1.5 gh issue list: #1 'Add obstacle detection unit tests' (enhancement) and #2 'Update README installation section' (documentation)",
            lambda: re.search(r"(?m)^#1\s+Add obstacle detection unit tests\s+enhancement\b", s15) is not None
            and re.search(r"(?m)^#2\s+Update README installation section\s+documentation\b", s15) is not None)
    t.check(2, "ANSWER-1 is a closing keyword (Closes, Fixes or Resolves)", lambda: _answer(ctx, 1).lower() in KEYWORDS)
    t.check(1, "live repo: your identity is set in this clone (not a placeholder, not a teammate's)",
            lambda: own_identity(ctx), needs_repo=True)
    url = f.remote_url("origin") if ctx.repo_mode else ""
    t.check(1, "live repo: origin is your own GitHub repository named rover-pr-lab (not the course repository)",
            lambda: bool(slug_of(url)) and slug_of(url) != COURSE_SLUG and slug_of(url).endswith("/" + REPO_NAME), needs_repo=True,
            why=lambda: "origin must be git@github.com:<you>/rover-pr-lab.git")
    t.check(1, "live repo: main tracks origin/main, your own repository",
            lambda: f.branch_config("main") == ("origin", "refs/heads/main") and slug_of(url) not in ("", COURSE_SLUG), needs_repo=True,
            why=lambda: "push with -u")
    return t


# -- Task 2 -----------------------------------------------------------------
def grade_task2(ctx: Ctx) -> Task:
    """Task 2: a feature branch, a pull request that closes an issue, a review comment and a fix."""
    t = Task(2, "Open a pull request", 25, ctx.repo_mode)
    f = ctx.facts
    mine = own_slug(ctx)
    s = {k: clean(ctx.step(k)) for k in ("2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8")}
    first, fix = _printed(s["2.1"]), _printed(s["2.6"])
    t.check(2, "2.1 commit output: '[feature/readme-usage <sha>] docs: add usage instructions to readme', 1 file changed",
            lambda: first is not None and first.group(1) == "feature/readme-usage" and first.group(3).strip() == USAGE_SUBJECT
            and re.search(r"\b1 file changed", s["2.1"]) is not None)
    t.check(1, "2.2 push output: '* [new branch]  feature/readme-usage -> feature/readme-usage'",
            lambda: re.search(r"\* \[new branch\]\s+feature/readme-usage -> feature/readme-usage", s["2.2"]) is not None)
    t.check(1, "2.2 push output: branch 'feature/readme-usage' set up to track 'origin/feature/readme-usage'",
            lambda: re.search(r"(?i)branch 'feature/readme-usage' set up to track (?:remote branch 'feature/readme-usage' from 'origin'"
                              r"|'origin/feature/readme-usage')", s["2.2"]) is not None)
    t.check(1, "2.2 the push went to your own repository", lambda: bool(mine) and to_slug(s["2.2"]) == mine)
    t.check(1, "2.2 GitHub's hint 'Create a pull request for feature/readme-usage' with its .../pull/new/feature/readme-usage address",
            lambda: "Create a pull request for 'feature/readme-usage'" in s["2.2"] and "/pull/new/feature/readme-usage" in s["2.2"])
    number = pr_number(ctx)
    t.check(3, "2.3 gh pr create: the address of the pull request in your own repository (.../pull/<number>)",
            lambda: number is not None and number >= 3)
    t.check(2, "2.4 gh pr list: your pull request, its title and its branch feature/readme-usage",
            lambda: number is not None and re.search(rf"(?m)^#{number}\s+{re.escape(USAGE_SUBJECT)}\s+feature/readme-usage\b", s["2.4"]) is not None)
    t.check(2, "2.5 gh pr review --comment: 'Reviewed pull request ...#<number>' (the same pull request)",
            lambda: number is not None and re.search(rf"Reviewed pull request \S*#{number}\b", s["2.5"]) is not None)
    t.check(2, "2.6 commit output: '[feature/readme-usage <sha>] docs: fix broken link in usage section', 1 insertion(+), 1 deletion(-)",
            lambda: fix is not None and fix.group(1) == "feature/readme-usage" and fix.group(3).strip() == FIXLINK_SUBJECT
            and re.search(r"\b1 file changed, 1 insertion\(\+\), 1 deletion\(-\)", s["2.6"]) is not None)
    rng = re.search(RANGE_RE, s["2.7"])
    t.check(2, "2.7 push output: '<first commit>..<fix commit>  feature/readme-usage -> feature/readme-usage' (the pull request got the new commit)",
            lambda: rng is not None and first is not None and fix is not None and rng.group(3) == "feature/readme-usage"
            and first.group(2).startswith(rng.group(1)[:7]) and fix.group(2).startswith(rng.group(2)[:7]))
    t.check(3, "2.8 gh pr view: 'wants to merge 2 commits into main from feature/readme-usage'",
            lambda: re.search(r"wants to merge 2 commits into main from feature/readme-usage", s["2.8"]) is not None)
    t.check(1, "2.8 gh pr view shows the description with 'Closes #2'", lambda: "Closes #2" in s["2.8"])
    a = f.rev(first.group(2)) if ctx.repo_mode and first else ""
    b = f.rev(fix.group(2)) if ctx.repo_mode and fix else ""
    t.check(4, "live repo: the two commits of 2.1 and 2.6 exist, the second is on top of the first, and the second has the link corrected "
               "(docs/install.md) where the first had the typo (docs/instal.md)",
            lambda: bool(a) and bool(b) and f.commit(a).subject == USAGE_SUBJECT and f.commit(b).subject == FIXLINK_SUBJECT  # type: ignore[union-attr]
            and f.commit(b).parents == [a] and "docs/instal.md" in (f.file_at(a, "README.md") or "")  # type: ignore[union-attr]
            and f.file_at(b, "README.md") == README_FIXED, needs_repo=True,
            why=lambda: "expected: a commit with the typo, then a commit on top of it that fixes the link")
    return t


# -- Task 3 -----------------------------------------------------------------
def grade_task3(ctx: Ctx) -> Task:
    """Task 3: squash, merge commit and rebase, and what each leaves in the history."""
    t = Task(3, "Three ways to merge", 25, ctx.repo_mode)
    f = ctx.facts
    mine = own_slug(ctx)
    s = {k: clean(ctx.step(k)) for k in ("3.1", "3.2", "3.3", "3.4", "3.5", "3.6")}
    squash_n = _merged(ctx, "3.1", "Squashed and merged", USAGE_SUBJECT)
    merge_n = _merged(ctx, "3.2", "Merged", DETECTOR_SUBJECT)
    rebase_n = _merged(ctx, "3.3", "Rebased and merged", CREEP_SUBJECT)
    t.check(3, "3.1 gh pr merge --squash: 'Squashed and merged pull request ...#<number> (docs: add usage instructions to readme)', "
               "the number of your first pull request",
            lambda: squash_n is not None and (pr_number(ctx) is None or squash_n == pr_number(ctx)))
    t.check(3, "3.2 gh pr merge --merge: 'Merged pull request ...#<number> (fix(vision): raise the detection threshold)'",
            lambda: merge_n is not None and squash_n is not None and merge_n > squash_n)
    t.check(3, "3.3 gh pr merge --rebase: 'Rebased and merged pull request ...#<number> (feat(control): add creep speed)'",
            lambda: rebase_n is not None and merge_n is not None and rebase_n > merge_n)
    t.check(3, "3.4 pull output: 'Updating <old>..<new>', 'Fast-forward', and README.md, src/detector.py, src/controller.py, docs/speeds.md changed",
            lambda: re.search(r"(?m)^Updating [0-9a-f]{7,40}\.\.[0-9a-f]{7,40}\s*$", s["3.4"]) is not None and "Fast-forward" in s["3.4"]
            and all(re.search(rf"(?m)^\s{re.escape(p)}\s+\|", s["3.4"]) for p in ("README.md", "src/detector.py", "src/controller.py", "docs/speeds.md")))
    g = s["3.5"]
    subjects = [strip_decoration(e.subject) for e in oneline_entries(g)]
    t.check(4, "3.5 graph: the squash commit '<title> (#<n>)', the merge commit 'Merge pull request #<n> from <you>/fix/detector-threshold' with its "
               "branch (| \\ and | /), the branch commit, and the two replayed commits",
            lambda: squash_n is not None and f"{USAGE_SUBJECT} (#{squash_n})" in subjects and merge_n is not None
            and any(x.startswith(f"Merge pull request #{merge_n} from ") and x.endswith("/fix/detector-threshold") for x in subjects)
            and DETECTOR_SUBJECT in subjects and CREEP_SUBJECT in subjects and CREEP_DOC_SUBJECT in subjects
            and re.search(r"(?m)^\|\\", g) is not None and re.search(r"(?m)^\|/", g) is not None)
    t.check(2, "3.6 branch -d and push --delete: 'Deleted branch feature/readme-usage' and '- [deleted] feature/readme-usage'",
            lambda: re.search(r"Deleted branch feature/readme-usage \(was [0-9a-f]{7,40}\)", s["3.6"]) is not None
            and re.search(r"- \[deleted\]\s+feature/readme-usage", s["3.6"]) is not None and to_slug(s["3.6"]) == mine)
    t.check(1, "ANSWER-2 is merge (a merge commit has two parents)", lambda: _answer(ctx, 2).lower().replace(" commit", "") == "merge")
    t.check(1, "ANSWER-3 is 1 (a squash and merge adds one commit)", lambda: _answer(ctx, 3) == "1")
    above = f.above_base() if ctx.repo_mode else []
    squash = next((c for c in above if squash_n and c.subject == f"{USAGE_SUBJECT} (#{squash_n})"), None)
    merge = next((c for c in above if merge_n and c.subject.startswith(f"Merge pull request #{merge_n} from ")), None)
    owner = mine.split("/")[0] if mine else ""
    t.check(1, "live repo: the squash commit '<title> (#<n>)' has one parent and the final README (with the link corrected)",
            lambda: squash is not None and len(squash.parents) == 1 and f.file_at(squash.sha, "README.md") == README_FIXED, needs_repo=True,
            why=lambda: "main has no single squashed commit for the pull request (a squash and merge makes one commit '<title> (#<n>)')")
    t.check(1, "live repo: the merge commit has two parents, and its second parent is 'fix(vision): raise the detection threshold'",
            lambda: merge is not None and len(merge.parents) == 2 and f.commit(merge.parents[1]).subject == DETECTOR_SUBJECT  # type: ignore[union-attr]
            and merge.subject.lower().startswith(f"merge pull request #{merge_n} from {owner.lower()}/fix/detector-threshold"), needs_repo=True)
    creep = next((c for c in above if c.subject == CREEP_SUBJECT), None)
    doc = next((c for c in above if c.subject == CREEP_DOC_SUBJECT), None)
    local = f.local_branch("feature/creep-speed") if ctx.repo_mode else ""
    t.check(2, "live repo: the two commits of the rebase merge sit one on top of the other, after the merge commit, and have new numbers "
               "(the commits on your local feature/creep-speed branch are different)",
            lambda: creep is not None and doc is not None and doc.parents == [creep.sha] and len(creep.parents) == 1
            and merge is not None and f.is_ancestor(merge.sha, creep.sha) and creep.sha != local and bool(local)
            and doc.sha != local, needs_repo=True,
            why=lambda: "expected the two commits of feature/creep-speed replayed on top of main (rebase and merge)")
    t.check(1, "live repo: the local branch feature/readme-usage is gone (after the squash merge)",
            lambda: squash is not None and not f.local_branch("feature/readme-usage"), needs_repo=True)
    return t


# -- Task 4 -----------------------------------------------------------------
def grade_task4(ctx: Ctx) -> Task:
    """Task 4: a contributing guide, and the issue that the merged pull request closed by itself."""
    t = Task(4, "The contributing guide and the closed issue", 15, ctx.repo_mode)
    f = ctx.facts
    mine = own_slug(ctx)
    s = {k: clean(ctx.step(k)) for k in ("4.1", "4.2", "4.3", "4.4")}
    t.check(3, "4.1 gh issue list --state closed: #2 'Update README installation section' (closed by the merged pull request)",
            lambda: re.search(r"(?m)^#2\s+Update README installation section\b", s["4.1"]) is not None)
    c = _printed(s["4.2"])
    t.check(2, "4.2 commit output: '[main <sha>] docs: add contributing guide', create mode CONTRIBUTING.md",
            lambda: c is not None and c.group(1) == "main" and c.group(3).strip() == CONTRIB_SUBJECT
            and "create mode 100644 CONTRIBUTING.md" in s["4.2"])
    t.check(2, "4.3 push output: '<old>..<new>  main -> main' (accepted, not rejected)",
            lambda: re.search(RANGE_RE, s["4.3"]) is not None and "! [" not in s["4.3"])
    t.check(1, "4.3 the push went to your own repository", lambda: bool(mine) and to_slug(s["4.3"]) == mine)
    t.check(2, "4.4 gh issue list: only #1 'Add obstacle detection unit tests' is still open",
            lambda: re.search(r"(?m)^#1\s+Add obstacle detection unit tests\b", s["4.4"]) is not None
            and re.search(r"(?m)^#2\s", s["4.4"]) is None)
    tip = f.with_subject(CONTRIB_SUBJECT) if ctx.repo_mode else None
    t.check(3, "live repo: CONTRIBUTING.md has the three sections (Branching strategy, Commit messages, Pull requests) with the lines of the handout",
            lambda: tip is not None and f.file_at(tip.sha, "CONTRIBUTING.md") == CONTRIBUTING, needs_repo=True,
            why=lambda: "CONTRIBUTING.md must be exactly the text of the handout")
    t.check(2, "live repo: the commit is on main, has one parent, and its number is the one pasted in 4.2",
            lambda: tip is not None and len(tip.parents) == 1 and c is not None and tip.sha.startswith(c.group(2)), needs_repo=True)
    return t


# -- Task 5 -----------------------------------------------------------------
def grade_task5(ctx: Ctx) -> Task:
    """Task 5: protect main, and see a direct push refused."""
    t = Task(5, "Protect main", 15, ctx.repo_mode)
    f = ctx.facts
    mine = own_slug(ctx)
    s = {k: clean(ctx.step(k)) for k in ("5.1", "5.2", "5.3", "5.4")}
    t.check(3, "5.1 gh api: GitHub's answer names '/branches/main/protection' and 'enforce_admins'",
            lambda: "/branches/main/protection" in s["5.1"] and "enforce_admins" in s["5.1"])
    t.check(2, "5.2 push output: '! [remote rejected]  main -> main'", lambda: re.search(r"! \[remote rejected\]\s+main -> main", s["5.2"]) is not None)
    t.check(1, "5.2 push output: 'error: failed to push some refs'", lambda: "error: failed to push some refs" in s["5.2"])
    t.check(1, "5.2 GitHub says why: the branch is protected (GH006 / 'Protected branch')",
            lambda: re.search(r"(?i)GH006|protected branch|GH013", s["5.2"]) is not None)
    t.check(1, "5.2 the rejected push was aimed at your own repository", lambda: bool(mine) and to_slug(s["5.2"]) == mine)
    t.check(2, "5.3 reset output: 'HEAD is now at <sha> docs: add contributing guide'",
            lambda: re.search(r"HEAD is now at [0-9a-f]{7,40} docs: add contributing guide", s["5.3"]) is not None)
    t.check(2, "5.4 status: 'Your branch is up to date with 'origin/main'' and a clean working tree",
            lambda: "Your branch is up to date with 'origin/main'" in s["5.4"] and "nothing to commit, working tree clean" in s["5.4"])
    t.check(3, "live repo: main is the same commit as origin/main, the line 'direct push test' is not in README.md, and the tree is clean",
            lambda: f.with_subject(CONTRIB_SUBJECT) is not None and f.main_tip() == f.rev("refs/remotes/origin/main") and bool(f.main_tip())
            and "direct push test" not in (f.file_at("HEAD", "README.md") or "") and f.working_tree_clean(), needs_repo=True,
            why=lambda: "undo the rejected commit with: git reset --hard origin/main")
    return t
