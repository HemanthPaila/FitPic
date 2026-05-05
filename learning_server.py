from flask import Flask, request, jsonify
from recommrender import get_personalized_recommendations, save_feedback

app = Flask(__name__)

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json

    results = get_personalized_recommendations(
        style=data["style"],
        occasion=data["occasion"],
        gender=data["gender"],
        good_colors=data["colors"]
    )

    return jsonify(results)


@app.route("/feedback", methods=["POST"])
def feedback():
    save_feedback(request.json)
    return jsonify({"message": "saved"})


app.run(port=5001, debug=True)
