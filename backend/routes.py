from app import app
from flask import request, jsonify
from csp import *
from astar import *
from genetic_algo import *

@app.route('/receive_json', methods=['POST', 'GET'])
def receive_json():
    try:
        data = request.json
        # print(data)
        path = []
        msg = ""
        try:
            label = data['label']
            
            # CSP Z3
            if label == "CSP(using Z3)":
                path = csp_z3(data)
                # print(path)

            # Astar
            elif label == "Heuristic(A*)":
                path = astar(data)
                # print(path)

            # Genetic Algo
            elif label == "Meta Heuristic(Genetic Algo)":
                path = genetic_algo(data)
                # print(path)

        except Exception as e:
            return jsonify({"error": str(e)}), 400 
        name = data.get("name")
        role = data.get("role")
        context = {
            "path": path,
            "msg": "This is success",
        }
        return jsonify(context), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400