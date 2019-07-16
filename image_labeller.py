"""Simple Flask app for checking the labels of images produced by
`auto-hasler`"""

import csv
import os

from typing import Generator
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

app = Flask(__name__)
# Secret key is needed to use Session.
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

GIVEN_LABELS_FILENAME = 'given_labels.csv'
OUTPUT_DATA_FILENAME = 'generated_labels.csv'
POLL_RESPONSES = {
    'Yes': 'yes',
    'Yes, wrong order': 'yes_wrong_order',
    'No': 'no',
}


def save_answer(answer):
    """Save the information stored in a request to the file, along with the
    username retrieved from session."""

    # Extract all information that we want to save.
    vote = answer.get('field')
    file_path = answer.get('file_path')
    given_labels = answer.get('given_labels')

    # If someone voted without providing an answer, we don't save it
    if vote is None:
        return

    to_be_saved = [
        file_path,
        POLL_RESPONSES[vote],
        given_labels,
    ]

    string = ','.join([str(_) for _ in to_be_saved]) + '\n'

    with open(OUTPUT_DATA_FILENAME, 'a') as out:
        out.write(string)


def get_image() -> Generator[Optional[Tuple[str, List[str]]], None, None]:
    """Return a new image to check."""

    files: List[Tuple[str, List[str]]] = []
    already_labelled_files: Set[str] = set()
    with open(OUTPUT_DATA_FILENAME, 'r') as f_out:
        reader = csv.reader(f_out)
        for row in reader:
            already_labelled_files.add(row[0])

    with open(os.path.join('static', 'data', GIVEN_LABELS_FILENAME),
              'r') as f_in:
        reader = csv.reader(f_in)
        for file_path, *given_labels in reader:
            # e.g. tests_pass.png,203,314
            if file_path not in already_labelled_files:
                files.append((file_path, given_labels))

    while files:
        yield files.pop()

    yield None


@app.route('/')
def index():
    """Main page: rendered when someone types localhost:5000"""
    return redirect(url_for('poll'))


@app.route('/poll', methods=['GET', 'POST'])
def poll():
    """Polling function: repeatedly asks questions about images"""

    poll_data = {
        'question': 'Are the given labels correct?',
        'fields': POLL_RESPONSES.keys(),
    }

    # Need to provide a new question
    if request.method == 'GET':
        new_image = get_image()
        next_ = next(new_image)
        if next_ is None:
            return redirect(url_for('done'))
        file_path, given_labels = next_
        return render_template('image_labels.html',
                               data=poll_data,
                               candidate_info={
                                   'file_path': file_path,
                                   'given_labels': given_labels,
                               })

    # The answer was provided by the user (request.method == 'POST')
    # Save and give the user another problem
    answer = request.form
    save_answer(answer)
    return redirect(url_for('poll'))


@app.route('/done')
def done():
    """Done page: tells the user they are done checking labels"""
    return render_template('done.html')


if __name__ == '__main__':
    app.run(debug=True)
