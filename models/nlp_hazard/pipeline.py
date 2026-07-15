"""
NLP Hazard Pipeline
===================
Loads the dslim/bert-base-NER model and applies keyword heuristics
to live news headlines to determine severity scores.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class HazardResult:
    headline: str
    locations: list[str]
    severity: float


def load_pipeline() -> tuple[None, Any]:
    """
    Lazy-load Hugging Face NER pipeline.
    Zero-shot classifier is replaced by a keyword heuristic.
    """
    from transformers import pipeline  # type: ignore[import-untyped]

    ner_pipeline = pipeline(
        "ner",
        model="dslim/bert-base-NER",
        aggregation_strategy="simple",
        device=-1,
    )
    # Return None for classifier to maintain signature compatibility
    return None, ner_pipeline


def compute_severity(headline: str) -> float:
    """
    Assign severity score based on regex word boundary keyword matching.
    """
    # Regex patterns for whole-word matching to prevent partial matches 
    # (e.g. avoiding matching "fire" inside "firewall")
    SEVERITY_TIERS = [
        (1.0, r'\b(murder|killed|stabbed|bomb|dead|death|shooting|shot)\b'),
        (0.8, r'\b(fire|accident|robbery|snatching|assault|injured|gutted|crash|rape)\b'),
        (0.6, r'\b(protest|waterlogging|flood|collapse|blocked|blocks|jam)\b'),
        (0.4, r'\b(traffic|disruption|delay|roadblock|disrupts|diverted)\b'),
        (0.2, r'\b(patrol|awareness|drill|advisory|warning)\b'),
    ]

    text_lower = headline.lower()
    for score, pattern in SEVERITY_TIERS:
        if re.search(pattern, text_lower):
            return score
    return 0.1  # Baseline for unclassified content


def classify_article(
    headline: str, 
    classifier: Any, 
    ner_pipeline: Any
) -> HazardResult | None:
    """
    Extract locations using BERT NER and score severity using keyword heuristics.
    """
    entities = ner_pipeline(headline)

    # Filter out broad city/state terms so we only get micro-locations
    IGNORE_LOCS = {"patna", "bihar", "india"}
    locations = [
        ent["word"] for ent in entities 
        if ent["entity_group"] == "LOC" and ent["word"].lower() not in IGNORE_LOCS
    ]

    # If no locations are found in the headline, it can't be mapped to the routing graph
    if not locations:
        return None

    severity = compute_severity(headline)

    return HazardResult(
        headline=headline,
        locations=locations,
        severity=severity,
    )
