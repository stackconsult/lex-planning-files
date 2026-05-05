"""Tests for Token Counter."""

import pytest
from datetime import datetime
from src.utils.token_counter import TokenCounter, TokenCount


class TestTokenCounter:
    def test_count_tokens(self):
        counter = TokenCounter()
        count = counter.count_tokens("api_search", "test content here")
        assert count.operation == "api_search"
        assert count.tokens == 3
        assert isinstance(count.timestamp, datetime)

    def test_count_tokens_stores(self):
        counter = TokenCounter()
        counter.count_tokens("api_search", "test")
        counts = counter._counts.get("api_search")
        assert len(counts) == 1

    def test_get_baseline(self):
        counter = TokenCounter()
        baseline = counter.get_baseline("api_search")
        assert baseline == 2500

    def test_get_baseline_nonexistent(self):
        counter = TokenCounter()
        baseline = counter.get_baseline("nonexistent")
        assert baseline is None

    def test_get_average_tokens(self):
        counter = TokenCounter()
        counter.count_tokens("api_search", "test content")
        counter.count_tokens("api_search", "more content here")
        avg = counter.get_average_tokens("api_search")
        assert avg == 2.5

    def test_get_average_tokens_nonexistent(self):
        counter = TokenCounter()
        avg = counter.get_average_tokens("nonexistent")
        assert avg is None

    def test_calculate_efficiency(self):
        counter = TokenCounter()
        counter.count_tokens("api_search", "test")
        efficiency = counter.calculate_efficiency("api_search")
        assert efficiency is not None
        assert 0 <= efficiency <= 1

    def test_calculate_efficiency_nonexistent(self):
        counter = TokenCounter()
        efficiency = counter.calculate_efficiency("nonexistent")
        assert efficiency is None

    def test_efficiency_reduction_calculation(self):
        counter = TokenCounter()
        # Baseline for api_search is 2500
        # If we use 1500 tokens, reduction = (2500-1500)/2500 = 0.4
        counter.count_tokens("api_search", "content " * 1500)
        efficiency = counter.calculate_efficiency("api_search")
        assert efficiency > 0
