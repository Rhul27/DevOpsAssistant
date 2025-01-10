import streamlit as st
import requests
from Core.func import *
from Core.database import get_command_history

# Function to fetch available models from the Ollama API
def fetch_models(ollama_url):
    try:
        response = requests.get(f"{ollama_url}/api/tags")
        if response.status_code == 200:
            return response.json()["models"]
        else:
            st.error(f"Failed to fetch models. Status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Invali Ollama URL. Error: {e}")
        return []

# Define the main function for the Streamlit app
def main():
    ssh = None
    st.set_page_config(page_title="DevOps Assistant", page_icon="🤖", layout="wide")
    st.title("🤖 DevOps Assistant")
    st.markdown("Welcome to the DevOps Assistant! Connect to your server and LLM model to get started.")
    # Sidebar for Ollama server URL and model selection
    st.sidebar.header("🔧 Configuration")
    server_host = get_local_ip()
    st.sidebar.write(f"Server Host: {server_host}")
    # Initialize ollama_url as None or an empty string
    ollama_url = st.sidebar.text_input("Ollama Server URL", placeholder="Enter Ollama Server URL (e.g., http://your-ollama-server:11434)")
    if ollama_url:
        models = fetch_models(ollama_url)
    else:
        models = [] 
    if models:
        model_names = [model["name"] for model in models]
        selected_model = st.sidebar.selectbox("Select a Model", model_names, index=0)
    else:
        selected_model = None

    if selected_model:
        model = connect_to_llm(selected_model, ollama_url)
        st.success(f"Connected to {selected_model} on Ollama Server at {ollama_url}")
    else:
        st.warning("No model selected. Please select a model from the dropdown menu.")

   # Sidebar for server connection details
    st.sidebar.header("🔐 Server Connection")
    ip = st.sidebar.text_input("IP Address", "192.168.1.100")
    username = st.sidebar.text_input("Username", "root")
    password = st.sidebar.text_input("Password", type="password")

    # Connect to the server
    if st.sidebar.button("🚀 Connect to Server"):
        if not ip or not username or not password:
            st.sidebar.error("Please fill in all the fields (IP, Username, Password).")
        else:
            with st.spinner("Connecting to the server..."):
                try:
                    ssh = connect_to_server(ip, username, password)
                    if ssh:
                        st.sidebar.success("✅ Connected to the server!")
                        st.session_state['ssh'] = ssh
                    else:
                        st.sidebar.error("❌ Failed to connect to the server.")
                except Exception as e:
                    st.sidebar.error(f"❌ An error occurred while connecting to the server: {e}")
    if 'ssh' in st.session_state and st.session_state['ssh'] is not None:
        st.sidebar.write(f"Connected to server: {ip}")
    else:
        st.sidebar.write("Not connected to the server.")

    # Button to switch to root user
    # if 'ssh' in st.session_state and st.session_state['ssh'] is not None:
    #     st.sidebar.header("🛠️ Root Access")
    #     if st.sidebar.button("🔑 Switch to Root User"):
    #         with st.spinner("Switching to root user..."):
    #             try:
    #                 become_root_user(ssh, password)
    #             except Exception as e:
    #                 st.error(f"Failed to switch to root user: {e}")

    # Button to switch to root user
    if 'ssh' in st.session_state and st.session_state['ssh'] is not None:
        st.sidebar.header("🛠️ Root Access")
        if st.sidebar.button("🔑 Switch to Root User"):
            with st.spinner("Switching to root user..."):
                try:
                    if st.session_state['ssh'] is None:
                        st.error("SSH connection is not established. Please connect to the server first.")
                    else:
                        become_root_user(st.session_state['ssh'], password)
                        st.success("Successfully switched to root user!")
                except Exception as e:
                    st.error(f"Failed to switch to root user: {e}")

    # Disconnect from the server
    if st.sidebar.button("🚫 Disconnect from Server"):
        if 'ssh' in st.session_state and st.session_state['ssh'] is not None:
            st.session_state['ssh'].close()
            st.session_state['ssh'] = None
            st.sidebar.success("Disconnected from the server.")
        else:
            st.sidebar.warning("Not connected to the server.")
    # Main content area
    st.header("💬 Ask a Question")
    question = st.text_input("Enter your question:", placeholder="e.g., How do I check disk usage on Linux?")

    if st.button("🚀 Submit"):
        if not question:
            st.error("Please enter a question.")
        # elif 'ssh' not in st.session_state or 'model' not in st.session_state:
        elif model is None:
            st.error("Please connect to both the server and the LLM model first.")
        else:
            with st.spinner("Processing your question..."):
                try:
                    response = ask_question_to_model(model, question)
                    if response:
                        st.write("📝 Response from the model:")
                        st.code(response, language="bash")
                        try:
                            results = extract_and_execute_commands(response, st.session_state['ssh'])
                            st.success("✅ Command execution completed.")
                            st.write("📊 Command Execution Summary:")
                            for i, result in enumerate(results, start=1):
                                st.write(f"**Command {i}:**")
                                st.code(result.get("output", "No output"), language="bash")
                                if result.get("error"):
                                    st.error(f"Error: {result.get('error')}")
                        except Exception as e:
                            st.error(f"❌ An error occurred while executing commands: {e}")
                    else:
                        st.error("❌ No response from the model.")
                except Exception as e:
                    st.error(f"❌ An error occurred while asking the question: {e}")

    # # Display command history
    # st.header("📜 Command History")
    # history = get_command_history()
    # if history:
    #     for entry in history:
    #         st.write(f"**Question:** {entry[1]}")
    #         st.code(entry[2], language="bash")
    #         st.write(f"**Timestamp:** {entry[3]}")
    #         st.write("---")
    # else:
    #     st.write("No command history available.")

# Run the Streamlit app
if __name__ == "__main__":
    main()