#!/usr/bin/env python

from flask import Flask, render_template, jsonify, request
import requests
import us
import json

app = Flask(__name__)
route_type = ''

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/states')
def get_states():
    return json.dumps([[state.abbr, state.name] for state in us.STATES])

@app.route('/routes/interstate')
def get_interstate_relations():
    # get route type parameter
    overpass_query = '[out:json];relation[network="US:I"][ref];out meta;'
    response = perform_overpass(overpass_query)
    relations = response.json()
    if 'elements' in relations and len(relations['elements']) > 0:
        out = process_elements(relations['elements'])
        return jsonify(out)
    return jsonify([])

@app.route('/routes/bicycle/<state_code>')
def get_bicycle_relations(state_code):
    # get route type parameter
    overpass_query = '[out:json];area[name="{statename}"]->.a;relation[route=bicycle][network](area.a);out meta;'.format(
        statename=us.states.lookup(state_code).name)
    response = perform_overpass(overpass_query)
    relations = response.json()
    if 'elements' in relations and len(relations['elements']) > 0:
        out = process_elements(relations['elements'])
        return jsonify(out)
    return jsonify([])

@app.route('/routes/state/<state_code>')
def get_relations(state_code):
    overpass_query = '[out:json];relation[network="US:{}"][ref];out meta;'.format(state_code.upper())
    response = perform_overpass(overpass_query)
    relations = response.json()
    if 'elements' in relations and len(relations['elements']) > 0:
        out = process_elements(relations['elements'])
        return jsonify(out)
    return jsonify([])

def process_elements(elements):
    out = []
    for element in elements:
        element = cleanup_element(element)
        out.append(element)
    return out

def perform_overpass(query):
    overpass_api_url = 'https://overpass-api.de/api/interpreter'
    payload = {'data': query}
    return requests.get(overpass_api_url, params=payload)

def cleanup_element(element):
    #print(element)
    osmid = element['id']
    # remove members we don't need em
    if 'members' in element:
        del element['members']        
    # flatten tags
    if 'tags' in element:
        for tag in element['tags']:
            element[tag] = element['tags'][tag]
    # delete original tags
    del element['tags']
    return element

if __name__ == "__main__":
    app.run()