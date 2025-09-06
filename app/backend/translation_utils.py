import re

def translate_and_extract_for_search(query):
    if not query:
        return '', 'no_translation'
    return query.strip(), 'english_direct'
