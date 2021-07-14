import os
from typing import List

import requests
from fixer import Fixer, FixerConfigurator, SentencesSplitter
from flask import Flask, render_template, send_from_directory, request, jsonify

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/fix', methods=['POST'])
def fix():
    default_configuration = get_default_configuration()

    for key, val in default_configuration.items():
        if isinstance(val, list) and f"{key}[]" in request.form:
            default_configuration[key] = request.form.getlist(f"{key}[]")
        else:
            default_configuration[key] = request.form.get(key, val, type=type(val))

    configuration = FixerConfigurator()
    configuration.load_from_dict(default_configuration)
    fixer = Fixer(configuration)

    src_text = request.form.get('source_text', '', type=str)
    trg_text = request.form.get('target_text', '', type=str)

    if trg_text:
        return fix_by_given_translation(src_text, trg_text, configuration, fixer)
    else:
        return get_translation_and_fix(src_text, configuration, fixer)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')


def fix_by_given_translation(src_text, trg_text, configuration, fixer):
    sentence, _, _ = fixer.fix(src_text, trg_text)

    result = {
        'cubbitt': None,
        'fixer': sentence
    }

    return jsonify(result)


def get_translation_and_fix(src_text, configuration, fixer):
    source_sentences_as_list = SentencesSplitter.split_text_to_sentences(src_text, configuration.source_lang, configuration)
    source_sentences_as_lines_string = make_string_from_split_sentences(source_sentences_as_list, configuration)
    cubbitt_translation = translate_at_cubbitt(source_sentences_as_lines_string, configuration.source_lang.acronym, configuration.target_lang.acronym)

    paragraphs = []

    for original_sentences, translated_sentences in zip(source_sentences_as_list, cubbitt_translation):
        paragraph = []
        for original_text, translated_text in zip(original_sentences, translated_sentences):
            translation, _, _ = fixer.fix(original_text, translated_text)
            paragraph.append(translation)

        paragraphs.append(" ".join(paragraph))

    result = {
        'cubbitt': "\n\n".join(" ".join(paragraph) for paragraph in cubbitt_translation),
        'fixer': "\n\n".join(paragraphs)
    }

    return jsonify(result)


def get_default_configuration():
    return {
        'source_lang': 'cs',
        'target_lang': 'en',
        'aligner': 'fast_align',
        'lemmatizator': 'udpipe_online',
        'names_tagger': 'nametag',
        'mode': 'fixing',
        'base_tolerance': 0.1,
        'approximately_tolerance': 0,
        'target_units': ['imperial', 'USD', 'F'],
        'exchange_rates': 'cnb',
        'tools': ['separators', 'units']
    }


def make_string_from_split_sentences(sentences: List[List[str]], configuration: FixerConfigurator):
    return "\n\n".join("\n".join(paragraph) for paragraph in sentences)


def translate_at_cubbitt(text: str, src_language: str, trg_language: str) -> List[List[str]]:
    cubbitt_request = requests.post(f"https://lindat.mff.cuni.cz/services/translation/api/v2/languages/?src={src_language}&tgt={trg_language}", {"input_text": text})
    cubbitt_request.encoding = 'utf-8'

    if cubbitt_request.status_code != 200:
        raise ConnectionError('Cannot connect to the LINDAT Translater.')

    paragraphs = []
    actual_paragraph = []
    for sentence in cubbitt_request.text.split("\n"):
        if not len(sentence) and actual_paragraph:
            paragraphs.append(actual_paragraph)
            actual_paragraph = []
        else:
            actual_paragraph.append(sentence)

    if actual_paragraph:
        paragraphs.append(actual_paragraph)

    return paragraphs


if __name__ == '__main__':
    app.run(debug=True)
