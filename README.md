DevOps Assistant 🤖
The DevOps Assistant is an AI-powered tool designed to help DevOps engineers and system administrators automate tasks, execute commands on remote servers, and generate accurate Bash commands using a local LLM (Large Language Model). It integrates with Streamlit for a user-friendly interface and uses SQLite for command history and caching.

Features ✨
SSH Integration: Connect to remote servers securely via SSH.

AI-Powered Command Generation: Use a local LLM (e.g., Ollama) to generate accurate Bash commands.

Command Execution: Execute commands on remote servers and view results in real-time.

Command History: Store and retrieve past commands and responses for future reference.

Caching Mechanism: Cache frequently used commands to improve response times.

User Authentication: Secure access with user authentication (optional).

Streamlit UI: Intuitive and interactive web-based interface.

Prerequisites 📋
Before running the DevOps Assistant, ensure you have the following installed:

Python 3.8+: Download Python

Ollama: A local LLM server. Install Ollama

Streamlit: For the web interface.

Paramiko: For SSH connections.

SQLite3: For database storage (included with Python).

Installation 🛠️
Clone the repository:

bash
Copy
git clone https://github.com/your-username/DevOpsAssistant.git
cd DevOpsAssistant
Install dependencies:

bash
Copy
pip install -r requirements.txt
Set up Ollama:

Install Ollama and start the server:

bash
Copy
ollama serve
Download a model (e.g., llama3.2):

bash
Copy
ollama pull llama3.2
Run the Streamlit app:

bash
Copy
streamlit run main.py
Access the app:

Open your browser and navigate to http://localhost:8501.

Usage 🚀
Connect to the Server:

Enter the server's IP address, username, and password in the sidebar.

Click "Connect to Server".

Connect to the LLM Model:

Select a model from the dropdown in the sidebar.

Click "Connect to LLM Model".

Ask a Question:

Enter your question in the main input box (e.g., "How do I check disk usage on Linux?").

Click "Submit" to get a response.

View Command History:

All executed commands and responses are stored in the database and displayed in the Command History section.

Folder Structure 📂
Copy
DevOpsAssistant/
├── Core/                     # Core functionality
│   ├── func.py               # SSH, LLM, and command execution
│   ├── database.py           # Database operations
│   ├── auth.py               # User authentication
│   └── utils.py              # Utility functions
├── models/                   # Data models
│   └── command_history.py    # SQLite model for command history
├── static/                   # Static files (CSS, images)
├── templates/                # HTML templates (if needed)
├── main.py                   # Streamlit app entry point
├── requirements.txt          # Python dependencies
└── devops_assistant.db       # SQLite database file
Configuration ⚙️
Ollama Server URL: Default is http://localhost:11434. Update in the sidebar if needed.

Default Model: Set to llama3.2. Change in func.py if required.

SSH Timeout: Default is 10 seconds. Adjust in func.py.

Contributing 🤝
Contributions are welcome! If you'd like to contribute, please follow these steps:

Fork the repository.

Create a new branch (git checkout -b feature/YourFeatureName).

Commit your changes (git commit -m 'Add some feature').

Push to the branch (git push origin feature/YourFeatureName).

Open a pull request.

License 📄
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments 🙏
Ollama: For providing the local LLM server.

Streamlit: For the easy-to-use web interface.

Paramiko: For SSH connectivity.
