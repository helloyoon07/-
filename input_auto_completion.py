import csv
import os
import heapq

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.freq = 0

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, freq):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.freq = freq

def build_trie_from_csv(csv_path):
    trie = Trie()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row['word'].strip().lower()
            try:
                freq = float(row['count'])
            except ValueError:
                continue
            trie.insert(word, freq)
    return trie

def autocomplete(trie, prefix, top_k=5, max_depth=5):
    node = trie.root
    for char in prefix:
        if char not in node.children:
            return []
        node = node.children[char]

    heap = []  # min-heap (freq, word)

    def dfs(current_node, path_chars, depth):
        if depth > max_depth:
            return
        if current_node.is_end:
            word = "".join(path_chars)
            if len(heap) < top_k:
                heapq.heappush(heap, (current_node.freq, word))
            elif current_node.freq > heap[0][0]:
                heapq.heapreplace(heap, (current_node.freq, word))

        for c, child in current_node.children.items():
            path_chars.append(c)
            dfs(child, path_chars, depth + 1)
            path_chars.pop()

    dfs(node, list(prefix), 0)

    result = sorted(heap, key=lambda x: x[0], reverse=True)
    return [(word, freq) for freq, word in result]

# 예시 사용법
csv_path = r"unigram_freq.csv"  # 실제 파일 경로
trie = build_trie_from_csv(csv_path)
print(autocomplete(trie, "happ", top_k=3))
