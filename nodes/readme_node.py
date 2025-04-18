import json
import os


# Load your API JSON data
def load_api_data(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            extracted_data = json.load(file)
        return extracted_data
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return None


# Prepare the prompt to generate README based on the project structure and JSON data
def prepare_readme_prompt(api_data, project_folder):
    prompt = "# Project Setup and Structure\n\n"
    prompt += "This README outlines the project setup, structure, and relevant details to get started with the FastAPI project.\n\n"


    # **Project Folder Structure** - Analyzing folder structure (files inside the FastAPI project folder)
    prompt += "## Project Folder Structure\n"
    for root, dirs, files in os.walk(project_folder):
        for file in files:
            if file.endswith(".py"):
                prompt += f"- **{os.path.relpath(os.path.join(root, file), project_folder)}**: Python source code file\n"
        for dir in dirs:
            prompt += f"- **{os.path.relpath(os.path.join(root, dir), project_folder)}**: Folder\n"
    prompt += "\n"


    # **Backend Logic** - If available, this will include logic defined in the JSON
    prompt += "## Backend Logic\n"
    backend_logic = api_data[0].get("backend_logic", [])
    if backend_logic:
        for logic in backend_logic:
            prompt += f"- {logic}\n"
    else:
        prompt += "No specific backend logic described.\n"
   
    prompt += "\n"


    # **Database Schema** - Extracting tables, columns, and relationships
    prompt += "## Database Schema\n"
    db_schema = api_data[0].get("database_schema", {})
    if db_schema:
        prompt += "### Tables and Columns\n"
        for table_name, table_info in db_schema.get("tables", {}).items():
            prompt += f"#### {table_name} Table\n"
            prompt += "Columns:\n"
            for column_name, column_type in table_info.get("columns", {}).items():
                prompt += f"- `{column_name}`: `{column_type}`\n"
            if table_info.get("primary_key"):
                prompt += f"Primary Key: `{table_info['primary_key']}`\n"
            if table_info.get("foreign_keys"):
                prompt += "Foreign Keys:\n"
                for fk in table_info.get("foreign_keys", []):
                    # Handle foreign key data gracefully
                    if isinstance(fk, dict):
                        # If it's a dictionary, try to access the 'table' and 'column' keys
                        table = fk.get('table', 'Unknown table')
                        column = fk.get('column', 'Unknown column')
                        prompt += f"- References `{table}` (`{column}`)\n"
                    elif isinstance(fk, str):
                        # If it's a string, handle it appropriately
                        prompt += f"- Foreign Key (String): {fk}\n"
                    elif isinstance(fk, list):
                        # If it's a list, iterate through it and process each item
                        prompt += f"- Foreign Key (List): {', '.join(fk)}\n"
                    else:
                        # If it's an unknown format, log it as unhandled
                        prompt += f"- Invalid foreign key format: {fk}\n"
    else:
        prompt += "No database schema available.\n"
    prompt += "\n"


    # **Authentication** - Include authentication and role-based access from the JSON
    prompt += "## Authentication\n"
    auth_info = api_data[0].get("authentication", {})
    if auth_info:
        prompt += f"**Authentication Type**: `{auth_info.get('type', 'Unknown')}`\n"
        if "roles" in auth_info:
            prompt += "Roles:\n"
            for role in auth_info.get("roles", []):
                prompt += f"- `{role}`\n"
        if "rules" in auth_info:
            prompt += "Rules:\n"
            for rule in auth_info.get("rules", []):
                prompt += f"- {rule}\n"
    else:
        prompt += "No authentication information available.\n"


    # **API Endpoints** - Mention key API endpoints
    prompt += "\n## Key API Endpoints\n"
    for entry in api_data:
        for endpoint in entry.get("api_endpoints", []):
            method = endpoint.get("method", "UNKNOWN")
            path = endpoint.get("path", "UNKNOWN")
            description = endpoint.get("description", "No description available.")
            prompt += f"- `{method}` {path}: {description}\n"
    prompt += "\n"


    # Return the final prompt
    return prompt


# Generate README using Llama or another AI model
def generate_readme_with_ai(prompt):
    # This is a mock-up of calling an AI model, e.g., Llama, to generate detailed content for the README
    # We will directly use the prompt as input and assume the AI generates a rich README output.
    # Replace with an actual AI API call if using a model like Llama, GPT-3, etc.
    generated_readme = f"# Auto-generated README\n\n{prompt}"
    return generated_readme


# Save the generated README to a markdown file
def save_readme_to_file(readme_content, project_folder):
    output_file_path = os.path.join(project_folder, "README.md")
    with open(output_file_path, "w", encoding="utf-8") as md_file:
        md_file.write(readme_content)
    print(f"✅ README saved to {output_file_path}")


# Main flow
def generate_readme(json_path, base_dir):
    # Load API data from the JSON file
    api_data = load_api_data(json_path)
    if api_data is None:
        return


    # Find the latest fastapi_project folder
    dirs = [d for d in os.listdir(base_dir) if d.startswith("fastapi_project_") and os.path.isdir(os.path.join(base_dir, d))]
    if not dirs:
        print("❌ No project folder found.")
        return
    dirs.sort(reverse=True)
    project_folder = os.path.join(base_dir, dirs[0])


    # Prepare the prompt for the README
    prompt = prepare_readme_prompt(api_data, project_folder)


    # Generate README using AI model (like Llama or GPT)
    readme_content = generate_readme_with_ai(prompt)


    # Save the generated README to the project folder
    save_readme_to_file(readme_content, project_folder)


# Define file paths
base_dir = os.getcwd()  # Get current working directory
json_file_path = os.path.join(base_dir, "extracted_data.json")


generate_readme(json_file_path, base_dir)


