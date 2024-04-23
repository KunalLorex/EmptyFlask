from flask import Flask, request, jsonify
from flask_cors import CORS
# from codesta import main

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def process_input():
    # Check if the request has JSON data
    if request.is_json:
        # Get the JSON data from the request body
        data = request.json
        # Check if the 'input' key exists in the JSON data
        if 'input' in data:
            # Get the value of the 'input' key
            input_text = data['input']
            # url=main(input_text)
            url="https://manimnioclass.s3.eu-north-1.amazonaws.com/Imagegen_demo_1.png"

            # Return the input text as JSON response
            return jsonify({'output': url})
        else:
            # If 'input' key is missing, return an error message
            return jsonify({'error': 'Input key not found'}), 400
    else:
        # If request is not JSON, return an error message
        return jsonify({'error': 'Request must be JSON'}), 400

if __name__ == '__main__':
    app.run(debug=True)
