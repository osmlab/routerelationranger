#!/usr/bin/env python

from flask import Flask, render_template, jsonify, request
import requests
import json
import pycountry
import us

app = Flask(__name__)
route_type = ''

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/countries')
def get_countries():
    return json.dumps([[c.alpha_2, c.name] for c in pycountry.countries])

@app.route('/states/<countrycode>')
def get_states(countrycode):
    try:
        states = [[s.code, s.name] for s in pycountry.subdivisions.get(country_code=countrycode)]
        return json.dumps(states)
    except KeyError:
        return jsonify([])
    return jsonify([])

@app.route('/routes/interstate/<country_code>')
def get_interstate_relations(country_code):
    # get route type parameter
    overpass_query = '[out:json];relation[network="{country_code}:I"][ref];out meta;'.format(country_code=country_code)
    print(overpass_query)
    response = perform_overpass(overpass_query)
    relations = response.json()
    if 'elements' in relations and len(relations['elements']) > 0:
        out = process_elements(relations['elements'])
        return jsonify(out)
    return jsonify([])

@app.route('/routes/bicycle/<country_code>/<state_code>')
def get_bicycle_relations(country_code, state_code):
    # get route type parameter
    overpass_query = '[out:json];area[name="{statename}"]->.a;relation[route=bicycle][network](area.a);out meta;'.format(
        statename=pycountry.subdivisions.get(code='{}-{}'.format(country_code, state_code)).name)
    print(overpass_query)
    response = perform_overpass(overpass_query)
    relations = response.json()
    if 'elements' in relations and len(relations['elements']) > 0:
        out = process_elements(relations['elements'])
        return jsonify(out)
    return jsonify([])

@app.route('/routes/state/<country_code>/<state_code>')
def get_relations(country_code, state_code):
    overpass_query = '[out:json];relation[network="{country_code}:{state_code}"][ref];out meta;'.format(
        country_code=country_code,
        state_code=state_code)
    print(overpass_query)
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

def split_code(state_code):
    # format is COUNTRY_CODE-STATE_CODE
    return state_code.split('-')

if __name__ == "__main__":
    app.run()