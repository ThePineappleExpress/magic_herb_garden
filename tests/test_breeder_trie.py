"""Tests for breeder_trie.py - breeder name autocomplete."""

import breeder_trie


def test_breeder_search_empty_prefix():
    assert breeder_trie.breeder_search("") == []


def test_breeder_search_whitespace_prefix():
    assert breeder_trie.breeder_search("   ") == []


def test_load_trie():
    """Trie loads from bin/db without error."""
    trie = breeder_trie.load_trie()
    assert isinstance(trie, dict)
    assert len(trie) > 0, "Trie should have entries"


def test_breeder_search_returns_list():
    result = breeder_trie.breeder_search("a")
    assert isinstance(result, list)


def test_breeder_search_results_start_with_prefix():
    result = breeder_trie.breeder_search("bar")
    for name in result:
        assert name.startswith("bar"), f"Expected '{name}' to start with 'bar'"


def test_breeder_search_limit():
    result = breeder_trie.breeder_search("a", limit=3)
    assert len(result) <= 3, f"Expected <=3 results, got {len(result)}"


def test_breeder_search_no_match():
    result = breeder_trie.breeder_search("zzzzxqqqq")
    assert result == [], f"Expected empty list for non-matching prefix, got {result}"


def test_breeder_search_mocked_trie():
    """Test with a controlled trie structure."""
    original = breeder_trie._TRIE
    try:
        mock = {"s": {"e": {"n": {"s": {"i": {"_end": True}}}}}}
        breeder_trie._TRIE = mock
        result = breeder_trie.breeder_search("sen")
        assert "sensi" in result
    finally:
        breeder_trie._TRIE = original


def test_breeder_search_case_insensitive():
    """Upper case prefix should still work (lowered internally)."""
    original = breeder_trie._TRIE
    try:
        mock = {"a": {"b": {"_end": True}}}
        breeder_trie._TRIE = mock
        result = breeder_trie.breeder_search("A")
        assert "ab" in result
    finally:
        breeder_trie._TRIE = original
