import strain_trie


def test_trie_search_empty_prefix():
    assert strain_trie.trie_search("") == []


def test_trie_search_whitespace_prefix():
    assert strain_trie.trie_search("   ") == []


def test_trie_search_mocked_trie():
    # build a tiny trie structure compatible with the module implementation
    mock = {"#": {"a": {"b": {"_end": True}, "c": {"_end": True}}}}
    # directly replace module _TRIE for environments without pytest fixtures
    original = strain_trie._TRIE
    try:
        strain_trie._TRIE = mock
        res = strain_trie.trie_search("a")
        assert "ab" in res or "ac" in res
    finally:
        strain_trie._TRIE = original


def test_load_trie():
    """Trie loads from bin/db without error."""
    trie = strain_trie.load_trie()
    assert isinstance(trie, dict)
    assert len(trie) > 0


def test_trie_search_returns_list():
    result = strain_trie.trie_search("a")
    assert isinstance(result, list)


def test_trie_search_limit():
    result = strain_trie.trie_search("a", limit=3)
    assert len(result) <= 3


def test_trie_search_no_match():
    result = strain_trie.trie_search("zzzzxqqqq")
    assert result == []


def test_trie_search_case_insensitive():
    """Upper case prefix should be lowered internally."""
    original = strain_trie._TRIE
    try:
        mock = {"#": {"x": {"y": {"_end": True}}}}
        strain_trie._TRIE = mock
        result = strain_trie.trie_search("X")
        assert "xy" in result
    finally:
        strain_trie._TRIE = original
