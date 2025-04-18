import json
import os
import re
import subprocess
import sys
from functools import lru_cache

# Optional: You can still install Groq package if not present
REQUIRED_PACKAGES = ["groq"]

def install_missing_packages():
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            print(f"📦 Installing missing package: {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

install_missing_packages()

from groq import Groq

# Set your Groq API key here
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Load extracted data
def load_extracted_data():
    try:
        with open("extracted_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: extracted_data.json not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Error: extracted_data.json is not valid JSON.")
        sys.exit(1)

# Groq API call wrapper
@lru_cache(maxsize=128)
def generate_test_code_from_llama3(prompt: str):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return ""

# Get the most recent project directory
def get_latest_project_dir():
    base_dir = os.getcwd()
    dirs = [d for d in os.listdir(base_dir) if d.startswith("fastapi_project_")]
    if not dirs:
        raise FileNotFoundError("❌ No fastapi_project_ folder found.")
    dirs.sort(reverse=True)
    return os.path.join(base_dir, dirs[0])

# Sanitize filenames to make them valid for filesystem
def sanitize_filename(path: str):
    path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
    return path if path else "root"

# Clean raw model response
def clean_response(text):
    # Removes any intro text before the first test case
    match = re.search(r"(?:^|\n)(\s*def\s+test_)", text)
    cleaned = text[match.start(1):] if match else text.strip()

    # Remove any trailing triple quotes or stray artifacts
    cleaned = re.sub(r"['\"]{3,}\s*$", "", cleaned).strip()

    # Remove comment lines starting with '''
    cleaned = re.sub(r"^\s*'''[^\n]*", "", cleaned, flags=re.MULTILINE)

    return cleaned

# Generate test files for components from the extracted JSON
def node_generate_tests():
    extracted_data = load_extracted_data()
    project_dir = get_latest_project_dir()
    test_dir = os.path.join(project_dir, "tests")
    os.makedirs(test_dir, exist_ok=True)

    # Process the list of extracted data
    for data in extracted_data:
        api_endpoints = data.get("api_endpoints", [])
        database_schema = data.get("database_schema", {})
        authentication = data.get("authentication", {})

        # Generate tests for API endpoints
        for endpoint in api_endpoints:
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", "/")
            description = endpoint.get("description", "")
            parameters = endpoint.get("parameters", [])

            file_name = f"test_{sanitize_filename(path)}.py"
            file_path = os.path.join(test_dir, file_name)

            prompt = f"""
Given this FastAPI endpoint:

Path: {path}
Method: {method}
Description: {description}
Parameters: {json.dumps(parameters)}

Write complete pytest unit tests to validate this endpoint.
- Include tests for both success and failure cases.
- Handle path and query parameters if provided.
- If authentication is needed, handle token and authentication scenarios.

ONLY return valid Python test code — no explanations or comments.
"""
            generate_test_file(file_path, prompt, endpoint)

        # Generate tests for database schema (tables and columns)
        tables = database_schema.get("tables", {})
        for table_name, table_details in tables.items():
            columns = table_details.get("columns", {})
            primary_key = table_details.get("primary_key", "")
            foreign_keys = table_details.get("foreign_keys", [])

            model_file_name = f"test_db_{sanitize_filename(table_name)}.py"
            model_file_path = os.path.join(test_dir, model_file_name)

            prompt = f"""
Given this database table schema:

Table: {table_name}
Columns: {json.dumps(columns)}
Primary Key: {primary_key}
Foreign Keys: {json.dumps(foreign_keys)}

Write complete pytest unit tests to validate CRUD operations and validations for this table schema.
Include edge cases, exception handling, and boundary conditions.

ONLY return valid Python test code — no explanations or comments.
"""
            generate_test_file(model_file_path, prompt, table_details)

        # Generate tests for authentication roles and rules
        if authentication:
            auth_type = authentication.get("type", "JWT")
            roles = authentication.get("roles", [])
            rules = authentication.get("rules", [])

            auth_file_name = "test_auth.py"
            auth_file_path = os.path.join(test_dir, auth_file_name)

            prompt = f"""
Given this authentication schema:

Authentication Type: {auth_type}
Roles: {json.dumps(roles)}
Rules: {json.dumps(rules)}

Write complete pytest unit tests to validate authentication.
Include tests for each role's access to the corresponding APIs and their restrictions.

ONLY return valid Python test code — no explanations or comments.
"""
            generate_test_file(auth_file_path, prompt, authentication)

# Function to generate the test file using the model output
def generate_test_file(file_path: str, prompt: str, context_data: dict):
    response_text = generate_test_code_from_llama3(prompt)
    clean_code = clean_response(response_text)

    # Collect models that are mentioned in the context data (API paths, params, or DB tables)
    imports = set()
    if "api_endpoints" in context_data:
        for endpoint in context_data["api_endpoints"]:
            path = endpoint.get("path", "")
            parameters = endpoint.get("parameters", [])
            for param in parameters:
                if param.get("type") in ["int", "str", "float"]:
                    continue  # Ignore simple data types, they don't need imports
                if param.get("type") in ["Pod", "User", "Session"]:  # Custom model checks
                    imports.add(param.get("type"))
    if "tables" in context_data:
        for table_name, table_details in context_data["tables"].items():
            columns = table_details.get("columns", {})
            for col_name, col_type in columns.items():
                if col_type in ["Pod", "User", "Session"]:
                    imports.add(col_type)

    # Add the necessary import statements for the models used in the test case
    import_statements = "\n".join([f"from app.models import {model}" for model in imports]) + "\n"

    # Add the import statement for the Groq client at the top
    groq_import = "from groq import Groq\nGROQ_API_KEY = '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'\nclient = Groq(api_key=GROQ_API_KEY)\n\n"

    # Comment out the last line of the generated code
    if clean_code.strip():
        clean_code = "\n".join(clean_code.splitlines()[:-1]) + "\n# " + clean_code.splitlines()[-1]

    # Write to the file with the cleaned code and import
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(import_statements + groq_import + clean_code)

    print(f"✅ Generated: {file_path}")

# Main execution
if __name__ == "__main__":
    node_generate_tests()


