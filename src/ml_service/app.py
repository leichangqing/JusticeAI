from flask import Flask, request, jsonify
from web.ml_controller import MlController
from util.log import Log
app = Flask(__name__)


@app.route("/predict", methods=['POST'])
def classify_claim_category():
    input_json = request.get_json()
    return jsonify(MlController.predict_outcome(input_json))


@app.route("/weights", methods=['POST'])
def classify_claim_category():
    return jsonify(MlController.get_classifier_weights())