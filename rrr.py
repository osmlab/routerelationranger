#!/usr/bin/env python

from flask import Flask, render_template, jsonify
import requests
import us
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/_states')
def get_states():
    return json.dumps(us.states.mapping('name', 'abbr'))

@app.route('/_routes/<state_code>')
def get_relations(state_code):
    overpass_api_url = 'https://overpass-api.de/api/interpreter'
    payload = {'data': '[out:json];relation[network="US:{}"];out meta;'.format(state_code.upper())}
    response = requests.get(overpass_api_url, params=payload)
    relations = response.json()
    print(relations)
    print(response.url)
    if 'elements' in relations and len(relations['elements']) > 0:
        return jsonify(relations['elements'])
    return '{}'

if __name__ == "__main__":
    app.run()
