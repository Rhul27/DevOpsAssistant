from langchain_ollama import OllamaLLM
import re
import paramiko
import logging
from typing import Optional, List, Dict, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)

# Constants
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"
DEFAULT_SSH_TIMEOUT = 10  # Timeout for SSH connections in seconds
command_cache = {}

# Custom Exceptions
class SSHConnectionError(Exception):
    pass

class ModelConnectionError(Exception):
    pass

class CommandExecutionError(Exception):
    pass

class InvalidResponseError(Exception):
    pass


def connect_to_server(ip: str, username: str, password: str, timeout: int = DEFAULT_SSH_TIMEOUT, port: int = 22) -> paramiko.SSHClient:
    """
    Connect to the server via SSH with error handling and timeout.

    Args:
        ip (str): The IP address of the server.
        username (str): The username for SSH login.
        password (str): The password for SSH login.
        timeout (int): SSH connection timeout in seconds.

    Returns:
        paramiko.SSHClient: The SSH connection object.

    Raises:
        SSHConnectionError: If the connection fails.
    """
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # try:
    #     ssh.connect(hostname=ip, username=username, password=password, timeout=timeout)
    #     logger.info(f"Connected to {ip} as {username}")
    #     return ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip, username=username, password=password, timeout=timeout, port=port)
        logger.info(f"Connected to {ip} as {username}")
        return ssh
    except Exception as e:
        logger.error(f"Failed to connect to {ip}: {e}")
        raise SSHConnectionError(f"SSH connection failed: {e}")

def become_root_user(ssh: paramiko.SSHClient, password: str) -> None:
    """
    Switch to root user by running sudo commands.

    Args:
        ssh (paramiko.SSHClient): The SSH connection.
        password (str): The password for sudo.

    Raises:
        CommandExecutionError: If switching to root fails.
    """
    try:
        stdin, stdout, stderr = ssh.exec_command("sudo -s")
        stdin.write(f"{password}\n")
        stdin.flush()
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            error = stderr.read().decode().strip()
            raise CommandExecutionError(f"Failed to switch to root user: {error}")
        logger.info("Switched to root user.")
    except Exception as e:
        logger.error(f"Failed to switch to root user: {e}")
        raise CommandExecutionError(f"Root user switch failed: {e}")

def connect_to_llm(model_name: str = DEFAULT_MODEL, ollama_url: str = DEFAULT_OLLAMA_URL) -> OllamaLLM:
    """
    Connects to a local LLM using the OllamaLLM class from langchain_ollama.

    Args:
        model_name (str): The name of the model to connect to.
        ollama_url (str): The URL of the Ollama server.

    Returns:
        OllamaLLM: The connected LLM object.

    Raises:
        ModelConnectionError: If the connection fails.
    """
    try:
        model = OllamaLLM(model=model_name, base_url=ollama_url)
        logger.info(f"Connected to the model: {model_name}")
        return model
    except Exception as e:
        logger.error(f"Failed to connect to the model: {e}")
        raise ModelConnectionError(f"Model connection failed: {e}")

def ask_question_to_model(model: OllamaLLM, question: str) -> Optional[str]:
    """
    Asks a question to the connected model and returns the response.
    Enhances filtering and ensures valid Bash commands are returned.

    Args:
        model (OllamaLLM): The connected LLM object.
        question (str): The question to ask the model.

    Returns:
        str: The response from the model.

    Raises:
        InvalidResponseError: If the model fails to respond or no valid commands are found.
    """
    if not model:
        logger.error("No model is connected. Please connect to a model first.")
        raise InvalidResponseError("No model connected.")

    # Check if the question is already in the cache
    if question in command_cache:
        logger.info(f"Returning cached response for: {question}")
        return command_cache[question]

    # Enhanced prompt for better Bash command generation
    enhanced_prompt = (
        f"You are a DevOps assistant. Your task is to generate accurate and efficient Bash commands. "
        f"Provide only the Bash command(s) inside triple backticks (```bash\n<command>\n```). "
        f"Do not include explanations or comments unless explicitly asked. "
        f"Here are some examples:\n"
        f"1. To list files in a directory: ```bash\nls -l\n```\n"
        f"2. To check disk usage: ```bash\ndf -h\n```\n"
        f"3. To find a file: ```bash\nfind /path/to/dir -name 'filename'\n```\n"
        f"Now, respond to the following request:\n{question}"
    )

    try:
        response = model.invoke(enhanced_prompt)
        logger.info(f"Response from the model: {response}")

        # Filter out non-Bash responses
        bash_commands = re.findall(r"```bash\n(.*?)\n```", response, re.DOTALL)
        if not bash_commands:
            logger.warning("No valid Bash commands found in the response. Regenerating...")
            response = model.invoke(f"Your previous response did not contain valid Bash commands. Please try again.\n{enhanced_prompt}")
            bash_commands = re.findall(r"```bash\n(.*?)\n```", response, re.DOTALL)
            if not bash_commands:
                raise InvalidResponseError("No valid Bash commands generated.")

        # Join commands into a single response
        filtered_response = "```bash\n" + "\n".join(bash_commands) + "\n```"
        
        # Cache the response for future use
        command_cache[question] = filtered_response
        return filtered_response
    except Exception as e:
        logger.error(f"Failed to get a response from the model: {e}")
        raise InvalidResponseError(f"Model response failed: {e}")

def execute_ssh_command(ssh: paramiko.SSHClient, command: str) -> Dict[str, Any]:
    """
    Executes a shell command on the remote server via SSH and returns the output.
    Enhances error handling and command validation.

    Args:
        ssh (paramiko.SSHClient): The SSH connection.
        command (str): The shell command to execute.

    Returns:
        dict: A dictionary containing the output, error, and exit status.

    Raises:
        CommandExecutionError: If the command execution fails.
    """
    try:
        # Validate the command to prevent dangerous operations
        if re.search(r"rm\s+-[rf]\s+/", command):  # Prevent 'rm -rf /'
            raise CommandExecutionError("Dangerous command detected: 'rm -rf /' is not allowed.")

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        exit_status = stdout.channel.recv_exit_status()
        result = {
            "output": output,
            "error": error,
            "exit_status": exit_status
        }
        logger.info(f"Command executed: {command}\nResult: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to execute command: {command}\nError: {e}")
        raise CommandExecutionError(f"Command execution failed: {e}")

def extract_and_execute_commands(response: str, ssh: paramiko.SSHClient) -> List[Dict[str, Any]]:
    """
    Extracts shell commands from the model response and executes them on the remote server.
    Enhances filtering, validation, and execution.

    Args:
        response (str): The text response containing shell commands.
        ssh (paramiko.SSHClient): The SSH connection.

    Returns:
        list: A list of dictionaries containing the results of each executed command.

    Raises:
        InvalidResponseError: If no commands are found in the response.
    """
    # Extract commands from triple backticks
    command_blocks = re.findall(r"```(?:bash)?\n(.*?)```", response, re.DOTALL)
    if not command_blocks:
        logger.error("No commands found in the model response.")
        raise InvalidResponseError("No commands found in the response.")

    results = []
    for block in command_blocks:
        commands = block.strip().split('\n')
        for command in commands:
            if command:  # Ensure the line is not empty
                # Remove '$' and '#' symbols
                clean_command = re.sub(r"[$#]", "", command).strip()
                if clean_command:  # Skip empty lines after cleaning
                    logger.info(f"Executing on remote server: {clean_command}")
                    try:
                        result = execute_ssh_command(ssh, clean_command)
                        results.append(result)
                    except CommandExecutionError as e:
                        logger.error(f"Command execution failed: {e}")
                        results.append({"command": clean_command, "error": str(e)})
    return results

def generate_command_summary(results: List[Dict[str, Any]]) -> str:
    """
    Generates a summary of executed commands and their results.

    Args:
        results (list): A list of command execution results.

    Returns:
        str: A formatted summary of the executed commands.
    """
    summary = "Command Execution Summary:\n"
    for i, result in enumerate(results, start=1):
        summary += f"\nCommand {i}:\n"
        summary += f"  Output: {result.get('output', 'No output')}\n"
        summary += f"  Error: {result.get('error', 'No error')}\n"
        summary += f"  Exit Status: {result.get('exit_status', 'Unknown')}\n"
    return summary
