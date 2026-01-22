# strain_trie.py
import json
import os

TRIE_FILE = "bin/db/seed_trie.json"  

def load_trie():
    path = os.path.join(os.path.dirname(__file__), TRIE_FILE)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

TRIE = load_trie()
END_MARKER = "_end"  

def _walk_prefix(trie, prefix):
    node = trie.get("#", trie)
    for character in prefix:
        character_lowercase = character.lower()
        if character_lowercase not in node:
            return None
        node = node[character_lowercase]
    return node

def _collect(node, prefix, out, limit):
    if len(out) >= limit:
        return
    if END_MARKER in node:
        out.append(prefix)
    for character, child in node.items():
        if character == END_MARKER:
            continue
        _collect(child, prefix + character, out, limit)

def trie_search(prefix, limit=20):
    prefix = prefix.strip().lower()
    if not prefix:
        return []

    node = _walk_prefix(TRIE, prefix)
    if node is None:
        return []

    out = []
    _collect(node, prefix, out, limit)
    return out