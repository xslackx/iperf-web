from flask import Flask, render_template, request, Response, jsonify
from pathlib import Path
from dotenv import dotenv_values
from flask_cors import CORS
from utils.cmds import ( str_to_boolean, run_command,
sanitize_parameters, validate_target, is_valid_port )

import json
import os

yes = { **dotenv_values('.cors') }
app = Flask(__name__)
cors = CORS(app,resources=yes["allow"])

app_port = os.getenv('IPERF_WEB_PORT', '5000')
debug_mode = str_to_boolean(os.getenv('IPERF_WEB_DEBUG_MODE', False))

# Route to display the page
@app.route('/')
def index():
    return render_template('index.html')

# Display available usage tools
@app.route('/get_tools')
def avail_tools():
    return {"tool_available": [ 'dig', 'iperf', 'mtr', 'nc',
                               'nslookup', 'ping', 'traceroute' ]}

# Route to obtain settings for a given test.
@app.route('/get_settings/<test_type>')
def get_settings(test_type):
    configFile = "config/config.json"
    if Path(configFile).is_file():
        with open(configFile, 'r') as f:
            settings = json.load(f)
    
        # Send only the relevant settings for the selected test_type
        return jsonify(settings.get(test_type, []))
    
    # Config file doesn't exist. Return an empty array
    return "[]"

# Route to handle form submission and execute selected test
@app.route('/run_test', methods=['POST'])
def run_test():
    test_type = request.form.get('test_type')
    output = ""
    sanitized_params = ""
    command = []

    # Only run tests for valid test types
    TEST_TYPES = {'dig', 'iperf', 'mtr', 'nc', 'nslookup', 'ping', 'traceroute'}
    if test_type in TEST_TYPES:
        target = request.form.get(test_type + '_target')
        # Validate the target address
        if not validate_target(target):
            return Response("'" + str(target) + "' is not a valid target address.", mimetype='text/plain')
        parameters = request.form.get(test_type + '_parameters', '')

        # MTR specific parameters
        if test_type == 'mtr':
            mtr_reportcycles = int(request.form.get('mtr_reportcycles', '200'))
            parameters += ' --report --report-wide --report-cycles ' + str(mtr_reportcycles)

        # netcat specific parameters
        if test_type == 'nc':
            port = request.form.get('nc_port')

            if not is_valid_port(port):
                return Response("'" + str(port) + "' is not a valid TCP port.", mimetype='text/plain')

            command = [test_type, '-vz', target, port]

        # netcat specific parameters
        if test_type == 'nslookup':
            server = request.form.get('nslookup_dns_server')
            if server:
                parameters = server
                sanitized_params = sanitize_parameters(parameters)
                command = [test_type, target] + sanitized_params

        # ping specific parameters
        if test_type == 'ping':
            count = int(request.form.get('ping_count', '4'))
            parameters += ' -c' + str(count)

        # iperf specific parameters
        if test_type == 'iperf':
            iperf_version = request.form.get('iperf_version')
            port = request.form.get('iperf_port')

            if not is_valid_port(port):
                port = 5001

            conn_type = request.form.get('iperf_conn_type')

            # Choose the correct iperf command based on version
            base_command = 'iperf3' if iperf_version == '3' else 'iperf'

            timeout = int(request.form.get('iperf_timeout', '10'))

            sanitized_params = sanitize_parameters(parameters)

            command = [base_command, '-c', target, '-p', port, '--forceflush', '-t', str(timeout)] + sanitized_params

            # Add -u flag for UDP connection type
            if conn_type == 'UDP':
                command.append('-u')

        if not sanitized_params:
            sanitized_params = sanitize_parameters(parameters)

        if not command:
            command = [test_type] + sanitized_params + [target]

        print(f"Executing command: {' '.join(command)}")  # Debugging statement

    return Response(run_command(command), mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=debug_mode,host='0.0.0.0',port=app_port)