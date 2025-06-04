from flask import Flask, request, jsonify, render_template
from tinydb import TinyDB, Query
from input_auto_completion import Trie, build_trie_from_csv, autocomplete, dijkstra_typo_correction
import csv

app = Flask(__name__)
db = TinyDB('db.json')
User = Query()
trie = build_trie_from_csv('unigram_freq.csv')
# HTML 렌더링 라우트
@app.route('/')
def index():
    return render_template('input.html')

# 자동완성 API 라우트
@app.route('/autocomplete')
def autocomplete_route():
    prefix = request.args.get('prefix', '').lower()
    if not prefix:
        return jsonify([])
    suggestions = autocomplete(trie, prefix, top_k=20)
    return jsonify([word for word, _ in suggestions])

@app.route('/typo_correction')
def typo_correction_route():
    input_word = request.args.get('word', '').lower()
    if not input_word:
        return jsonify([])

    max_cost = int(request.args.get('max_cost', 2))
    top_k = int(request.args.get('top_k', 10))
    weight_cost = float(request.args.get('weight_cost', 1.0))
    weight_freq = float(request.args.get('weight_freq', 0.1))
    min_freq = int(request.args.get('min_freq', 100000))

    results = dijkstra_typo_correction(
        trie,
        input_word=input_word,
        max_cost=max_cost,
        top_k=top_k,
        weight_cost=weight_cost,
        weight_freq=weight_freq,
        min_freq=min_freq
    )

    # priority 기준 정렬
    results.sort(key=lambda x: x[3])

    return jsonify([
        {
            "word": word,
            "cost": cost,
            "freq": freq,
            "priority": round(priority, 4)
        }
        for word, cost, freq, priority in results
    ])

@app.route('/check_words', methods=['POST'])
def check_words():
    data = request.get_json()
    words = data.get('words', [])

    # 예시 trie에서 빈도수 가져오기 (빈도 없으면 0으로 처리)
    freqs = {}
    for w in words:
        freqs[w] = trie.get_frequency(w) or 0

    return jsonify(freqs)


if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=True)

