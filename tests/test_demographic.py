"""Tests for services.demographic — M_demo matrix correctness."""

from services.demographic import get_demographic_multiplier


def test_male_day():
    assert get_demographic_multiplier("male", 12) == 1.00


def test_male_night():
    assert get_demographic_multiplier("male", 22) == 0.80


def test_female_day():
    assert get_demographic_multiplier("female", 10) == 0.90


def test_female_night():
    assert get_demographic_multiplier("female", 23) == 0.67


def test_boundary_day_start():
    """8 AM should be classified as 'day'."""
    assert get_demographic_multiplier("male", 8) == 1.00


def test_boundary_night_start():
    """8 PM (20:00) should be classified as 'night'."""
    assert get_demographic_multiplier("male", 20) == 0.80


def test_case_insensitive():
    """Gender input should be case-insensitive."""
    assert get_demographic_multiplier("Female", 14) == 0.90
    assert get_demographic_multiplier("MALE", 14) == 1.00


def test_unknown_gender_defaults_to_male():
    """Unknown gender should default to male (conservative)."""
    assert get_demographic_multiplier("other", 12) == 1.00
