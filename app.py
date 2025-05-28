from flask import Flask, request, jsonify, render_template
from tinydb import TinyDB, Query
from input_auto_completion import Trie, build_trie_from_csv, autocomplete
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
    suggestions = autocomplete(trie, prefix, top_k=10)
    return jsonify([word for word, _ in suggestions])

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=True)

