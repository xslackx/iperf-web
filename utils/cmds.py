import subprocess
import shlex
import select
import re

# function to convert a string to boolean
def str_to_boolean(s):
    return str(s).lower() == "true"

# Function to run a command and stream the output
def run_command(command):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError as e:
        yield f"Error: {str(e)}<br>"
        return
    except OSError as e:
        yield f"Error: {str(e)}<br>"
        return

    yield 'Executing command: ' + ' '.join(command) + '<br><br>'

    # Monitor both stdout and stderr streams
    while True:
        # Use select to monitor stdout and stderr
        reads = [process.stdout, process.stderr]
        readable, _, _ = select.select(reads, [], [])

        for stream in readable:
            if stream == process.stdout:
                stdout_line = process.stdout.readline().decode('utf-8')
                if stdout_line:
                    yield stdout_line + '<br>'

            if stream == process.stderr:
                stderr_line = process.stderr.readline().decode('utf-8')
                if stderr_line:
                    yield f"<span style='color:red;'>{stderr_line}</span><br>"

        # Break if the process has terminated and there's no more output
        if process.poll() is not None:
            break

    # Ensure that any remaining output is read after the process terminates
    remaining_stdout = process.stdout.read().decode('utf-8')
    if remaining_stdout:
        yield remaining_stdout + '<br>'
    
    remaining_stderr = process.stderr.read().decode('utf-8')
    if remaining_stderr:
        yield f"<span style='color:red;'>{remaining_stderr}</span><br>"

    yield '<br>Execution finished!<br>'

# Helper function to sanitize parameters
def sanitize_parameters(parameters):
    sanitized = shlex.split(parameters)  # Split safely without executing
    return sanitized

# Helper function to validate target addresses (e.g., IP or domain)
def validate_target(target):
    # Only allow alphanumeric, dots, hyphens (for domains) and IP addresses
    if re.match(r"^[a-zA-Z0-9.-]+$", target):
        return True
    return False

def is_valid_port(port):
    try:
        port = int(port)
        return 1 <= port <= 65535
    except (ValueError, TypeError):
        return False