import os

from fixer import Fixer, FixerConfigurator
from flask import Flask, render_template, send_from_directory, request

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

    src_text = request.form.get('source_text', '', type=str)
    trg_text = request.form.get('target_text', '', type=str)

    configuration = FixerConfigurator()
    configuration.load_from_dict(default_configuration)
    fixer = Fixer(configuration)
    translation, _ = fixer.fix(src_text, trg_text)

    # there was no fix or the sentence is unfixable
    if not translation or translation is True:
        translation = trg_text

    return translation


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')


def get_default_configuration():
    return {
        'source_lang': 'cs',
        'target_lang': 'en',
        'aligner': 'fast_align',
        'lemmatizator': 'udpipe_online',
        'names_tagger': 'nametag',
        'mode': 'recalculating',
        'base_tolerance': 0.1,
        'approximately_tolerance': 0.1,
        'target_units': ['imperial', 'USD', 'F'],
        'exchange_rates': 'cnb',
        'tools': ['separators', 'units']
    }
