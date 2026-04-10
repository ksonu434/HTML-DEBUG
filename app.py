import os
from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_data():
    url = request.form.get('url', '').strip()
    html_data = request.form.get('html_code', '')
    custom_regex = request.form.get('custom_regex', '').strip()
    
    if url:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            html_data = response.text
        except Exception as e:
            return jsonify({'Error_Logs': [f'URL Fetch Failed: {str(e)}']})

    extraction_patterns = {
        'M3U8_Streams': r'(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*)',
        'AES_Keys': r'#EXT-X-KEY:.*?URI=["\']?(https?://[^\s"\'<>]+)["\']?',
        'TS_Segments': r'(https?://[^\s"\'<>]+?\.ts[^\s"\'<>]*)',
        'Video_Files': r'(https?://[^\s"\'<>]+?\.(?:mp4|mkv|avi)[^\s"\'<>]*)',
        'Documents': r'(https?://[^\s"\'<>]+?\.pdf[^\s"\'<>]*)',
        'Images': r'(https?://[^\s"\'<>]+?\.(?:png|jpg|jpeg|webp|svg)[^\s"\'<>]*)',
        'Stylesheets': r'(https?://[^\s"\'<>]+?\.css[^\s"\'<>]*)',
        'Scripts': r'(https?://[^\s"\'<>]+?\.js[^\s"\'<>]*)'
    }
    
    if custom_regex:
        try:
            re.compile(custom_regex)
            extraction_patterns['Custom_Matches'] = custom_regex
        except re.error:
            return jsonify({'Error_Logs': ['Invalid Custom Regex Pattern.']})

    results = {}
    for cat, pat in extraction_patterns.items():
        matches = list(set(re.findall(pat, html_data)))
        if matches:
            results[cat] = matches
            
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
