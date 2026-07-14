"""
NLP Hazard Classification Pipeline
====================================
DESIGN.md §2B: Hugging Face zero-shot classification + NER to extract
incident severity and spatial references from news articles.

Uses a two-stage approach:
    1. Zero-shot classifier → Is this article about a safety hazard?
    2. NER → Extract location names from positive articles.
"""

from __future__ import annotations

from dataclasses import dataclass


# Candidate labels for zero-shot classification
HAZARD_LABELS = [
    "crime",
    "accident",
    "flood",
    "fire",
    "protest",
    "construction hazard",
    "safe / irrelevant",
]

# Threshold for considering an article as a genuine hazard
HAZARD_CONFIDENCE_THRESHOLD = 0.45


@dataclass
class HazardResult:
    """Structured output from the NLP pipeline."""
    headline: str
    predicted_label: str
    confidence: float
    locations: list[str]
    severity: float  # Normalised 0–1


def load_pipeline():
    """
    Lazy-load Hugging Face pipelines to avoid slow import-time downloads.

    Returns
    -------
    tuple
        (zero_shot_classifier, ner_pipeline)
    """
    # NOTE: Import here to keep module import fast
    from transformers import pipeline  # type: ignore[import-untyped]

    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1,  # CPU
    )
    ner = pipeline(
        "ner",
        model="dslim/bert-base-NER",
        aggregation_strategy="simple",
        device=-1,
    )
    return classifier, ner


def classify_article(
    text: str,
    classifier,
    ner_pipeline,
) -> HazardResult | None:
    """
    Run zero-shot classification and NER on a single article.

    Returns None if the article is classified as safe/irrelevant.
    """
    # Stage 1: zero-shot classification
    result = classifier(text, candidate_labels=HAZARD_LABELS)
    top_label = result["labels"][0]
    top_score = result["scores"][0]

    if top_label == "safe / irrelevant" or top_score < HAZARD_CONFIDENCE_THRESHOLD:
        return None

    # Stage 2: NER for location extraction
    entities = ner_pipeline(text)
    locations = [
        ent["word"]
        for ent in entities
        if ent["entity_group"] == "LOC"
    ]

    return HazardResult(
        headline=text[:120],
        predicted_label=top_label,
        confidence=top_score,
        locations=locations,
        severity=top_score,  # Use confidence as a proxy for severity
    )
