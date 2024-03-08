import spacy
import gensim

def topic_modeling(parsed_json):
    user_text = ""
    assistant_text = ""
    for log in parsed_json:
        if log['role'] == 'assistant':
            assistant_text += log['content']
        else:
            user_text += log['content']
    
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(user_text)
    
