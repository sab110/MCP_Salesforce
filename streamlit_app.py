import os
import json
import sys
# Add 'src' to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import re
import requests
import streamlit as st
import asyncio

import salesforcemcp.sfdc_client as sfdc_client
import salesforcemcp.definitions as sfmcpdef
import salesforcemcp.implementations as sfmcpimpl

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

from dotenv import load_dotenv
load_dotenv()

server = Server("salesforce-mcp")

sf_client = sfdc_client.OrgHandler()
if not sf_client.establish_connection():
    print("❌ Failed to initialize Salesforce connection")
else:
    print("✅ Salesforce connection established.")

# sf_client = sfdc_client.OrgHandler()
# sf_client.establish_connection()

tool_map = {tool.name: tool for tool in sfmcpdef.get_tools()}


def generate_tool_doc():
    lines = [
        "You are a helpful assistant for Salesforce MCP tools.",
        "Your job is to interpret user requests and call the correct tool once all arguments are available",
        "Parse with:\nrun: <tool_name>\nargs: { ... }",
        "Use only the tools below:\n"
    ]
    for tool in tool_map.values():
        lines.append(f"- {tool.name}: {tool.description}")
        required = tool.inputSchema.get("required", [])
        if required:
            lines.append(f"  Required: {', '.join(required)}")
    return "\n".join(lines)


# def sanitize_json(text):
#     text = text.replace("“", "\"").replace("”", "\"")
#     text = re.sub(r",\s*}", "}", text)
#     text = re.sub(r",\s*]", "]", text)
#     return text

def sanitize_json(text):
    # Replace curly quote marks
    text = text.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

    # Convert keys like object_name: "value" → "object_name": "value"
    text = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1 "\2":', text)

    # Remove trailing commas
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    return text

async def run_tool(tool_name, args):
    impl = {
        "create_object": sfmcpimpl.create_object_impl,
        "create_object_with_fields": sfmcpimpl.create_object_with_fields_impl,
        "create_custom_field": sfmcpimpl.create_object_with_fields_impl,
        "delete_object_fields": sfmcpimpl.delete_object_fields_impl,
        "create_custom_metadata_type": sfmcpimpl.create_custom_metadata_type_impl,
        "create_custom_metadata_field": sfmcpimpl.create_custom_metadata_type_impl,
        "create_tab": sfmcpimpl.create_tab_impl,
        "create_custom_app": sfmcpimpl.create_custom_app_impl,
        "create_report_folder": sfmcpimpl.create_report_folder_impl,
        "create_dashboard_folder": sfmcpimpl.create_dashboard_folder_impl,
        "run_soql_query": sfmcpimpl.run_soql_query_impl,
        "run_sosl_search": sfmcpimpl.run_sosl_search_impl,
        "get_object_fields": sfmcpimpl.get_object_fields_impl,
        "create_record": sfmcpimpl.create_record_impl,
        "update_record": sfmcpimpl.update_record_impl,
        "delete_record": sfmcpimpl.delete_record_impl,
        "describe_object": sfmcpimpl.describe_object_impl,
    }
    return impl[tool_name](sf_client, args)


# Set up session state
if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "system", "content": generate_tool_doc()}]

st.title("🤖 Salesforce MCP Assistant (LLM Chat UI)")

# Display message history
for msg in st.session_state.chat[1:]:  # skip system
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
if user_input := st.chat_input("Ask anything about Salesforce MCP..."):
    print("User Input:",user_input)
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-4.1-mini",
                        "messages": st.session_state.chat,
                        "temperature": 0.3
                    }
                )

                res_json = response.json()
                if "choices" not in res_json:
                    st.error(f"❌ LLM error: {res_json.get('error', 'Unknown')}")
                    st.stop()

                content = res_json["choices"][0]["message"]["content"]
                print("Content:",content)
                st.session_state.chat.append({"role": "assistant", "content": content})

                # If tool is selected
                if content.startswith("run"):
                    try:
                        lines = content.strip().split("\n", 1)
                        tool_name = lines[0].replace("run:", "").strip()
                        print("Tool_name:", tool_name)
                        args = json.loads(sanitize_json(lines[1].replace("args:", "").strip()))
                        print("Args:",args)

                        tool_result = asyncio.run(run_tool(tool_name, args))
                        print("Tool_result:",tool_result)
                        output = "\n".join(r.text for r in tool_result if r.type == "text")

                        # summarize output using LLM
                        summary = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": "openai/gpt-4.1-mini",
                                "messages": [
                                    {"role": "system", "content": "You are a helpful assistant summarizing Salesforce query results.\n"
                                    "The user asked a question, and the system responded with raw data from Salesforce.\n"
                                    "Your task is to translate that raw data into a clear, concise, natural language summary that directly answers the user's question. Provide Salesforce URLs only when available.\n"
                                    "Avoid repeating raw JSON, query syntax, or technical jargon."},
                                    {"role": "user", "content": f"User query: {user_input}\n\nSalesforce response:\n{output}"}
                                ]
                            }
                        ).json()

                        final_response = summary["choices"][0]["message"]["content"]
                        st.markdown(final_response)
                        print("Final Response:",final_response)
                        st.session_state.chat.append({"role": "assistant", "content": final_response})
                    except Exception as e:
                        st.error(f"Tool Error: {e}")
                        # st.session_state.chat.append({"role": "assistant", "content": f"Tool error: {e}"})
                else:
                    st.markdown(content)

            except Exception as e:
                st.error(f"Request failed: {e}")
