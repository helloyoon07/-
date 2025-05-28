import csv
import os
# Trie 노드 정의
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.freq = 0

# Trie 정의
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

# CSV에서 데이터 읽고 Trie에 삽입
def build_trie_from_csv(csv_path):
    trie = Trie()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row['word'].strip().lower()
            try:
                freq = float(row['count'])
            except ValueError:
                continue  # 숫자 변환 안 되면 무시
            trie.insert(word, freq)
    return trie
# 힙 정렬에 필요한 함수들

def heapify(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left][0] > arr[largest][0]:
        largest = left
    if right < n and arr[right][0] > arr[largest][0]:
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def build_max_heap(arr):
    n = len(arr)
    for i in range(n // 2 -1, -1, -1):
        heapify(arr, n, i)

def heap_sort(arr):
    n = len(arr)
    build_max_heap(arr)
    for i in range(n-1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  # 맨 뒤와 루트 교환
        heapify(arr, i, 0)

# autocomplete 함수 수정
import heapq

def autocomplete(trie, prefix, top_k=5, max_depth=10):
    node = trie.root
    for char in prefix:
        if char not in node.children:
            return []
        node = node.children[char]

    heap = []  # min-heap (freq, word)

    def dfs(node, path, depth):
        if depth > max_depth:
            return
        if node.is_end:
            if len(heap) < top_k:
                heapq.heappush(heap, (node.freq, path))
            else:
                if node.freq > heap[0][0]:
                    heapq.heapreplace(heap, (node.freq, path))

        for c, child in node.children.items():
            dfs(child, path + c, depth + 1)

    dfs(node, prefix, 0)

    result = sorted(heap, key=lambda x: x[0], reverse=True)
    return [(word, freq) for freq, word in result]



csv_path = r"unigram_freq.csv"  # 실제 파일 경로
trie = build_trie_from_csv(csv_path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(autocomplete(trie, "happ", top_k=3))
print("hi")