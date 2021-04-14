import os

from flask import Flask, render_template, send_from_directory, request, jsonify

from fixer import Fixer

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/fix', methods=['POST'])
def fix():
    src_lang = request.args.get('src', 'cs', type=str)
    trg_lang = request.args.get('trg', 'en', type=str)

    src_text = request.form.get('source_text', '', type=str)
    trg_text = request.form.get('target_text', '', type=str)

    class Arguments:

        def __init__(self, source_lang: str, target_lang: str):
            self.recalculate = False
            self.approximately = True
            self.source_lang = source_lang
            self.target_lang = target_lang

    fixer = Fixer(Arguments(src_lang, trg_lang))
    translation, _ = fixer.fix(src_text, trg_text)

    # there was no fix or the sentence is unfixable
    if not translation or translation is True:
        translation = trg_text

    return translation


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')
