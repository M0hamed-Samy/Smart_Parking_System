from requirments import *

@app.route("/api/face/recognize", methods=["POST"])
def face_recognize():

    if 'image' not in request.files:
        return jsonify({"error": "no image uploaded"})

    image = request.files['image']

    os.makedirs("images/temp", exist_ok=True)

    path = f"images/temp/{image.filename}"
    image.save(path)

    result = recognize(path, "images/faces/known")

    return jsonify({
        "result": result
    })