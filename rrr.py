#!/usr/bin/env python

from flask import Flask, render_template, jsonify
import requests
import us
import json
import iso8601

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/_states')
def get_states():
    return json.dumps([[state.abbr, state.name] for state in us.STATES])

@app.route('/_routes/<state_code>')
def get_relations(state_code):
    overpass_api_url = 'https://overpass-api.de/api/interpreter'
    payload = {'data': '[out:json];relation[network="US:{}"][ref];out meta;'.format(state_code.upper())}
    response = requests.get(overpass_api_url, params=payload)
    relations = response.json()
    out = []
    if 'elements' in relations and len(relations['elements']) > 0:
        for element in relations['elements']:
            # print(element)
            # remove members we don't need em
            del element['members']
            # flatten tags
            if 'tags' in element:
                for tag in element['tags']:
                    element[tag] = element['tags'][tag]
            # delete original tags
            del element['tags']
            if 'user' in element:
                element['user'] = '<a href="https://osm.org/user/{user}">{user}</a>'.format(user=element['user'])
            if 'changeset' and 'timestamp' in element:
                dt = iso8601.parse_date(element['timestamp'])
                datestring = dt.strftime('%Y-%m-%d %I:%M%p')
                element['timestamp'] = '<a href="https://www.openstreetmap.org/changeset/{changeset}">{datestring}</a>'.format(
                    changeset=element['changeset'],
                    datestring=datestring)
                #element['timestamp'] = '{datestring}'.format(datestring=datestring)
            out.append(element)
        return jsonify(out)
    return jsonify([])

if __name__ == "__main__":
    app.run()
