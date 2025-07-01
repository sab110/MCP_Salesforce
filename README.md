# 🚀 Salesforce MCP Assistant

A conversational assistant powered by LLMs to explore and interact with your Salesforce organization using natural language prompts. It turns complex Salesforce tasks into smooth, human-like conversations directly from a chat interface.

## 📖 Overview

The **Salesforce MCP Assistant** uses OpenRouter LLMs (e.g., GPT-4.1 mini) to intelligently interpret user inputs, identify the right Metadata Control Plane (MCP) tool, execute queries or administrative actions via Salesforce APIs, and return structured, user-friendly summaries.

Clickable URLs in responses provide direct access to Salesforce records in Lightning UI, making navigation seamless. Built-in session memory allows the assistant to maintain context across turns for coherent, personalized conversations.

## 🎯 Purpose

This assistant simplifies Salesforce data exploration by letting users query, list, and retrieve object metadata without writing SOQL. It’s designed for both technical and non-technical users who want to access Salesforce data conversationally.

Key capabilities include:
- Listing records from Salesforce objects.
- Counting records.
- Retrieving field metadata.
- Generating clickable record links.
- Summarizing query results in plain English.

## ✅ Requirements

- Python 3.10+
- Salesforce Org credentials (username, password, security token, domain, instance URL)
- OpenRouter API Key (for LLM responses)
- Hosting platform like Railway (or local execution)

## 🔐 Environment Variables

Create a `.env` file (or copy from `.env.example`) with:

```env
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_salesforce_security_token
SF_DOMAIN=login
SF_INSTANCE_URL=https://your-instance.lightning.force.com
OPENROUTER_API_KEY=your_openrouter_api_key
```

## ⚙️ Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/sab110/MCP_Salesforce.git
   cd MCP_Salesforce
   ```

2. **Set up a virtual environment and install dependencies**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**  
   Update `.env` with your Salesforce credentials and OpenRouter key.

4. **Launch the assistant**  
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

## 🛠 Tool Architecture

- `salesforcemcp/` contains MCP tool logic:
  - `implementations.py`: Tool functions.
  - `definitions.py`: Tool metadata.
  - `sfdc_client.py`: Salesforce connection and query execution.
- `streamlit_app.py` drives the chat interface.
- Tools are listed dynamically using metadata, dispatched via function maps, and summarized via LLMs.

## 💬 Streamlit Features

- Chat-style UI with threaded conversations.
- Realtime assistant responses with clickable Salesforce record URLs.
- LLM summaries for raw tool outputs.
- Console logs for debugging.

## 🚀 Deployment

Deploy on **Railway** or similar platforms:

1. Connect your GitHub repo to a Railway project.
2. Configure environment variables (SF_USERNAME, SF_PASSWORD, etc.).
3. In Railway deployment settings, set the start command:
   ```bash
   streamlit run streamlit_app.py --server.port=8081 --server.headless=true
   ```
4. Ensure Railway networking uses port 8081.
5. Enable "Wait for CI" in Railway’s GitHub integration for auto-redeploy on every push.

## 🛠 Customization Guide

To adapt the assistant for specific clients:
- Update `.env` with client-specific Salesforce credentials and OpenRouter API key.

## 📁 Directory Structure

```
src/
├── assets/
├── salesforcemcp/
│   ├── __init__.py
│   ├── definitions.py
│   ├── implementations.py
│   ├── sfdc_client.py
│   └── server.py
├── streamlit_app.py
├── requirements.txt
├── .env.example
└── pyproject.toml
```

## ✨ Credits

Built and customized by request for client-specific Salesforce assistant usage.
