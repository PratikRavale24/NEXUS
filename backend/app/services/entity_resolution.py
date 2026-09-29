from __future__ import annotations

import re
from difflib import SequenceMatcher


def normalize_text(value: str) -> str:
    """
    Normalize text for comparison.
    """
    value = value.lower().strip()

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def token_overlap(
    left: str,
    right: str,
) -> float:
    left_tokens = set(normalize_text(left).split())
    right_tokens = set(normalize_text(right).split())

    if not left_tokens or not right_tokens:
        return 0.0

    intersection = left_tokens & right_tokens

    return len(intersection) / max(
        len(left_tokens),
        len(right_tokens),
    )


def initial_last_name_match(
    mention: str,
    candidate: str,
) -> bool:
    """
    Handles variants such as:
    R. Patil -> Rohan Patil
    """

    mention_tokens = normalize_text(
        mention
    ).split()

    candidate_tokens = normalize_text(
        candidate
    ).split()

    if len(mention_tokens) < 2:
        return False

    if len(candidate_tokens) < 2:
        return False

    mention_first = mention_tokens[0]
    mention_last = mention_tokens[-1]

    candidate_first = candidate_tokens[0]
    candidate_last = candidate_tokens[-1]

    return (
        len(mention_first) == 1
        and mention_first == candidate_first[0]
        and mention_last == candidate_last
    )


def calculate_similarity(
    mention: str,
    candidate: str,
) -> float:

    mention_norm = normalize_text(mention)
    candidate_norm = normalize_text(candidate)

    if mention_norm == candidate_norm:
        return 1.0

    if initial_last_name_match(
        mention,
        candidate,
    ):
        return 0.95

    mention_tokens = mention_norm.split()
    candidate_tokens = candidate_norm.split()

    # Strong first-name + last-name match despite
    # additional middle-name/token information.
    if (
        len(mention_tokens) >= 2
        and len(candidate_tokens) >= 2
        and mention_tokens[0] == candidate_tokens[0]
        and mention_tokens[-1] == candidate_tokens[-1]
    ):
        return 0.93

    sequence_score = SequenceMatcher(
        None,
        mention_norm,
        candidate_norm,
    ).ratio()

    overlap_score = token_overlap(
        mention,
        candidate,
    )

    return (
        0.65 * sequence_score
        + 0.35 * overlap_score
    )


def resolve_person(
    mention: str,
    candidates: list[dict],
) -> dict:

    ranked = []

    for candidate in candidates:

        score = calculate_similarity(
            mention,
            candidate["name"],
        )

        ranked.append(
            {
                "person_id": candidate["person_id"],
                "canonical_name": candidate["name"],
                "score": round(score, 4),
            }
        )

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    best = ranked[0] if ranked else None

    if best is None:
        return {
            "mention": mention,
            "resolved": False,
            "person_id": None,
            "canonical_name": None,
            "score": 0.0,
            "review_required": True,
            "candidates": [],
        }

    score = best["score"]

    if score >= 0.90:
        status = "AUTO_RESOLVED"
        review_required = False

    elif score >= 0.75:
        status = "REVIEW_REQUIRED"
        review_required = True

    else:
        status = "UNRESOLVED"
        review_required = True

    return {
        "mention": mention,
        "resolved": status != "UNRESOLVED",
        "person_id": best["person_id"],
        "canonical_name": best["canonical_name"],
        "score": score,
        "status": status,
        "review_required": review_required,
        "candidates": ranked[:3],
    }