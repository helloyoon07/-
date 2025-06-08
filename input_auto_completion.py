import csv
import os

class TrieNode: # Trie 노드 정의
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.freq = 0

class Trie: # Trie 정의
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

def build_trie_from_csv(csv_path): # CSV에서 데이터 읽고 Trie에 삽입
    trie = Trie()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row['word'].strip().lower()
            try:
                freq = float(row['count'])
            except ValueError:
                continue  # 데이터 중 숫자 변환 안 되는 값은  무시
            trie.insert(word, freq)
    return trie

# 힙 정렬을 구현하기 위한 함수 heapify, build_max_heap, heap_sort
def heapify(arr, n, i): #서브트리에서 가장 큰 값이 위로 오게 만듦.
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left][0] > arr[largest][0]:
        largest = left
    if right < n and arr[right][0] > arr[largest][0]:
        largest = right

    if largest != i:  #largest가 변경되었으면 현재 노드와 바꾸고, 재귀 호출
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def build_max_heap(arr): #주어진 배열을 최대 힙으로 변환
    n = len(arr)
    for i in range(n // 2 -1, -1, -1):  #n//2부터 시작하는 이유는 리프 노드는 heapify할 필요가 없기 때문.
        heapify(arr, n, i)

def heap_sort(arr): #최대 힙을 이용해 정렬된 배열을 생성. (내림차순 → 뒤집으면 오름차순 가능).
    n = len(arr)
    build_max_heap(arr)
    for i in range(n-1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)


def autocomplete(trie, prefix, top_k): #필수인자: Trie 객체, prefix(접두어), 선택인자: 표시할 추천입력 개수수
    memo = {}  # 메모이제이션: 이미 방문한 TrieNode 결과를 저장하여 중복 탐색 방지 -> 사용되는 메모리 양을 줄이기 위함!

    def dfs(node, path):
        if node in memo:
            return memo[node]

        results = []
        if node.is_end:
            results.append((node.freq, path))
        for char, child in node.children.items():
            results.extend(dfs(child, path + char))

        memo[node] = results
        return results

    node = trie.root  # prefix를 Trie에서 따라 내려가며 해당 노드 탐색
    for char in prefix:
        if char not in node.children:
            return []
        node = node.children[char]
    results = dfs(node, prefix) # 해당 노드에서부터 가능한 모든 단어 탐색
    heap_sort(results) # 빈도수 기준으로 힙 정렬 수행 (heap_sort는 오름차순 정렬)
    results.reverse()  # 내림차순으로 바꾸기 위해 reverse (빈도 높은 순으로)
    return [(word, freq) for freq, word in results[:top_k]]

import math
import heapq
import os

def dijkstra_typo_correction(trie, input_word, max_cost=2, top_k=20, 
                             weight_cost=1.0, weight_freq=0.1,
                             min_freq=1000000):
    def get_priority(cost, freq):
        log_freq = math.log10(freq + 1) if freq > 0 else 0
        return weight_cost * cost - weight_freq * log_freq

    heap = []
    visited = set()
    seen_paths = set()
    results = []

    heapq.heappush(heap, (0, 0, 0, 0, id(trie.root), trie.root, ""))

    while heap and len(results) < top_k:
        priority, cost, neg_log_freq, pos, node_id, node, path = heapq.heappop(heap)
        state_id = (pos, node_id)

        if state_id in visited:
            continue
        visited.add(state_id)

        if pos == len(input_word) and node.is_end and path not in seen_paths:
            if cost <= max_cost and node.freq >= min_freq:
                seen_paths.add(path)
                freq = node.freq
                results.append((path, cost, freq, priority))
            continue

        # (1) 문자 일치
        if pos < len(input_word):
            ch = input_word[pos]
            if ch in node.children:
                child = node.children[ch]
                # 완화된 조건
                freq = child.freq if child.is_end else 0
                new_priority = get_priority(cost, freq)
                heapq.heappush(heap, (
                    new_priority, cost, -math.log(freq + 1),
                    pos + 1, id(child), child, path + ch
                ))

        # (2) 문자 교체
        if pos < len(input_word):
            for c, child in node.children.items():
                if c != input_word[pos]:
                    freq = child.freq if child.is_end else 0
                    new_priority = get_priority(cost + 1, freq)
                    heapq.heappush(heap, (
                        new_priority, cost + 1, -math.log(freq + 1),
                        pos + 1, id(child), child, path + c
                    ))

        # (3) 문자 삭제
        if pos < len(input_word):
            freq = node.freq if node.is_end else 0
            new_priority = get_priority(cost + 1, freq)
            heapq.heappush(heap, (
                new_priority, cost + 1, -math.log(freq + 1),
                pos + 1, node_id, node, path
            ))

        # (4) 문자 삽입
        for c, child in node.children.items():
            freq = child.freq if child.is_end else 0
            new_priority = get_priority(cost + 1, freq)
            heapq.heappush(heap, (
                new_priority, cost + 1, -math.log(freq + 1),
                pos, id(child), child, path + c
            ))

    return results


# 아래는 예시 실행 부분
csv_path = r"unigram_freq.csv"  # 파일 경로
trie = build_trie_from_csv(csv_path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 절대경로 설정
print(autocomplete(trie, "happ", top_k=3))

results = dijkstra_typo_correction(
    trie,
    input_word="loe",
    max_cost=3,
    top_k=5,
    weight_cost=1.0,
    weight_freq=0.1,
    min_freq=1000000
)
results.sort(key=lambda x: x[3])


for word, cost, freq, priority in results:
    print(f"추천 단어: {word}, 편집비용: {cost}, 빈도수: {freq}, priority: {priority:.4f}")