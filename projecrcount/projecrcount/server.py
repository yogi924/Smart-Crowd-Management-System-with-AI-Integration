# server.pyq
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)


gate_counts = {1: 0, 2: 0, 3: 0}


gate_locations = {
    1: {'lat': 28.637837093024938, 'lng': 77.37822128540587},
    2: {'lat': 28.63890283190635, 'lng': 77.37585341448568},
    3: {'lat': 28.63891615357386, 'lng': 77.37221053614691},
}

@app.route('/')
def index():
    return render_template('f.html')

@app.route('/update_count', methods=['POST'])
def update_count():
    data = request.get_json()
    gate_id = data.get('gate_id')
    count = data.get('count')
    if gate_id in gate_counts:
        gate_counts[gate_id] = count
    return jsonify(success=True)

@app.route('/get_counts')
def get_counts():
    return jsonify(gate_counts)

@app.route('/get_gate_locations')
def get_gate_locations():
    return jsonify(gate_locations)

# def fixed_gate_updates():
#     while True:
#         gate_counts[2] = 0
#         gate_counts[3] = 0  
#         time.sleep(3)        

if __name__ == '__main__':
   # threading.Thread(target=fixed_gate_updates, daemon=True).start()
    app.run(debug=True)
