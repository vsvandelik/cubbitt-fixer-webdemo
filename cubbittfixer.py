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
    if 'src' in request.args.keys():
        default_configuration.source_lang = FixerConfigurator.get_language(request.args, 'src')

    if 'trg' in request.args.keys():
        default_configuration.source_lang = FixerConfigurator.get_language(request.args, 'trg')

    src_text = request.form.get('source_text', '', type=str)
    trg_text = request.form.get('target_text', '', type=str)

    fixer = Fixer(default_configuration)
    translation, _ = fixer.fix(src_text, trg_text)

    # there was no fix or the sentence is unfixable
    if not translation or translation is True:
        translation = trg_text

    return translation


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')


def get_default_configuration():
    default_config = {
        'source_lang': 'cs',
        'target_lang': 'en',
        'aligner': 'fast_align',
        'lemmatizator': 'udpipe',
        'names_tagger': 'nametag',
        'mode': 'recalculating',
        'base_tolerance': 0.1,
        'approximately_tolerance': 0.1,
        'target_units': ['Imperial', 'USD', 'F'],
        'exchange_rates': 'cnb'
    }

    configuration = FixerConfigurator()
    configuration.load_from_dict(default_config)

    return configuration
