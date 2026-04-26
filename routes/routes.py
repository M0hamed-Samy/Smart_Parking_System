from requirments import *

@app.route("/")
def home():
    return jsonify({
        "message": "Smart Parking System Running 🚀",
        "status": "online"
    })
    
    
@app.route("/start", methods=["GET"])
def start_system():
    return jsonify({
        "system": "started"
    })
    
@app.route("/stop")
def stop():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return "Server shutting down..."