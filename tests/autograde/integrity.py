"""Detects pasted output that does not belong to the repository being graded."""
from __future__ import annotations

import re
from typing import List, Set

from .context import Ctx
from .facts import COURSE_SLUG, slug_of
from .tasks import TO_LINE_RE, URL_RE, clean, own_slug
from .textutil import line_shas

BRACKET_SHA_RE = re.compile(r"\[[^\]]*? ([0-9a-f]{7,40})\]")
RANGE_SHA_RE = re.compile(r"(?m)^\s+([0-9a-f]{7,40})\.\.([0-9a-f]{7,40})\s")
UPDATING_SHA_RE = re.compile(r"(?m)^Updating ([0-9a-f]{7,40})\.\.([0-9a-f]{7,40})\s*$")
EXTRA_SHA_RE = re.compile(r"(?:\(was |HEAD is now at )([0-9a-f]{7,40})")


def integrity_warnings(ctx: Ctx) -> List[str]:
    """Return human-readable warnings; an empty list means the pasted text matches this repository."""
    if not ctx.repo_mode:
        return []
    facts = ctx.facts
    live = slug_of(facts.remote_url("origin"))
    warnings: List[str] = []
    wrong: Set[str] = set()
    foreign: Set[str] = set()
    for text in ctx.steps.values():
        text = clean(text)
        for match in TO_LINE_RE.finditer(text):
            target = slug_of(match.group(1))
            if target and live and target != live:
                wrong.add(target)
        for match in re.finditer(URL_RE, text):
            target = f"{match.group(1)}/{match.group(2)}".lower()
            if live and target != live and target != COURSE_SLUG:
                wrong.add(target)
        tokens = line_shas(text) + BRACKET_SHA_RE.findall(text) + EXTRA_SHA_RE.findall(text)
        for pair in RANGE_SHA_RE.findall(text) + UPDATING_SHA_RE.findall(text):
            tokens += list(pair)
        for token in tokens:
            if not facts.commit_exists(token):
                foreign.add(token)
    if wrong:
        warnings.append("a pasted push or GitHub address names another repository than this clone's origin: " + ", ".join(sorted(wrong)))
    if foreign:
        warnings.append(f"{len(foreign)} commit SHA(s) in the pasted text do not exist in this repository "
                        f"(e.g. {', '.join(sorted(foreign)[:6])}); the outputs were not produced in this clone")
    return warnings


__all__ = ["integrity_warnings", "own_slug"]
