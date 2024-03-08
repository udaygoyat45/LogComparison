from werkzeug.utils import secure_filename

from flask import Flask, request
from flask_cors import CORS

from pymongo import MongoClient
import bson
import json
import re
import os


class LazyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)


def parse_text(text):
    pass

app = Flask(__name__)
CORS(app, supports_credentials=True)

class DevelopmentConfig:
    def __init__(self):
        self.UPLOAD_FOLDER = './uploads' 

config = DevelopmentConfig()
db = MongoClient('mongodb://localhost:27017').languagelog

@app.route('/')
def ping():
    return {'message': 'hello world'}


@app.route('/logs/list')
def list_logs():
    logs = list(db.logs.find())
    print(logs)
    display_logs = []
    for log in logs:
        display_logs.append({
            '_id': log['_id'],
            'name': log['name'],
            'type': log['type']
        })

    return {'logs': display_logs}


@app.route('/logs/content/<id>/<index>')
def log_content(id, index):
    log = db.logs.find_one({"_id": id})

    with open(log['location']) as fin:
        content = json.load(fin)
    
    content = content['conversation'][index]
    content = content.replace('"', "'")

    contents = content.split('}\n {')
    json_content = []


    for i in range(len(contents)):
        contents[i] = contents[i].replace("'content'", '"content"')
        contents[i] = contents[i].replace("'role'", '"role"')
        contents[i] = contents[i].replace("'user'", '"user"')
        contents[i] = contents[i].replace("'assistant'", '"assistant"')
        contents[i] = contents[i].replace('"content": \'', '"content": "')
        contents[i] = contents[i].replace('"content": \'', '"content": "')
        contents[i] = contents[i].replace("', \"role\":", "\", \"role\":")

        if i == 0:
            parsed_content = contents[i][1:] + '}'
        elif i == len(contents) - 1:
            parsed_content = '{' + contents[i][:-1]
        else:
            parsed_content = '{' + contents[i] + '}'
        
        json_content.append(json.loads(parsed_content, cls=LazyDecoder))
    

    return {'content': json_content[::-1]}


@app.route('/logs/upload', methods=['GET', 'POST'])
def upload_log():
    if request.method == 'POST':
        if 'file' not in request.files:
            return {'error': "No file detected"}

        file = request.files['file']
        if file.filename == '':
            return {'error': "No file detected"}

        if file:
            filename = secure_filename(file.filename)
            file_type = file.headers['Content-Type']
            file_location = os.path.join(config.UPLOAD_FOLDER, filename)
            file.save(file_location)

            new_media = {
                '_id': str(bson.objectid.ObjectId()),
                'name': filename,
                'type': file_type,
                'location': file_location,
            }

            db.logs.insert_one(new_media)
        
        return {'success': 'The file was successfuly uploaded', 
                'newLog': {
                    '_id': new_media['_id'],
                    'name': filename,
                    'type': file_type
                    }
                }

    return {'error': 'not a post request'}


@app.route('/logs/summary/<id>')
def summarize(id):
    log = db.logs.find_one({"_id": id})
    with open(log['location']) as fin:
        content = json.load(fin) 

    conversations = {conversation_id: {} for conversation_id in content['conversation_id']}
    for convo_id in content['conversation_id']:
        conversations[convo_id]['length'] = len(content['conversation'][convo_id])
        # conversations[convo_id]['convo'] = content['conversation'][convo_id]
    
    return {"data": conversations}



@app.route('/logs/topics/', methods=['GET', 'POST'])
def topic_modeling():
    if request.method == 'POST':
        data = request.get_json()
        selected_ids = data['selectedLogs']



        # log = db.logs.find_one({"_id": id})

        # with open(log['location']) as fin:
        #     content = json.load(fin)
        
        # content = content['conversation'][index]
        # content = content.replace('"', "'")

        # contents = content.split('}\n {')
        # json_content = []


        # for i in range(len(contents)):
        #     contents[i] = contents[i].replace("'content'", '"content"')
        #     contents[i] = contents[i].replace("'role'", '"role"')
        #     contents[i] = contents[i].replace("'user'", '"user"')
        #     contents[i] = contents[i].replace("'assistant'", '"assistant"')
        #     contents[i] = contents[i].replace('"content": \'', '"content": "')
        #     contents[i] = contents[i].replace('"content": \'', '"content": "')
        #     contents[i] = contents[i].replace("', \"role\":", "\", \"role\":")

        #     if i == 0:
        #         parsed_content = contents[i][1:] + '}'
        #     elif i == len(contents) - 1:
        #         parsed_content = '{' + contents[i][:-1]
        #     else:
        #         parsed_content = '{' + contents[i] + '}'
            
        #     json_content.append(json.loads(parsed_content, cls=LazyDecoder))
        
