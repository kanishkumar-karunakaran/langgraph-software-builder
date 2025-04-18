import json
import os
from transformers import LlamaTokenizer, LlamaForCausalLM


# Step 1: Load your API JSON data
def load_api_data(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            extracted_data = json.load(file)
        return extracted_data
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return None


# Step 2: Prepare the prompt to generate documentation
def prepare_prompt(api_data):
    prompt = "Generate API documentation for the following endpoints:\n"
    for entry in api_data:
        for endpoint in entry.get("api_endpoints", []):
            method = endpoint.get("method", "UNKNOWN")
            path = endpoint.get("path", "UNKNOWN")
            description = endpoint.get("description", "No description available.")
            parameters = endpoint.get("parameters", [])
            
            prompt += f"\n### {method} {path}\n"
            prompt += f"**Description**: {description}\n"
            
            if parameters:
                prompt += "**Parameters**:\n"
                for param in parameters:
                    name = param.get("name", "Unnamed")
                    param_type = param.get("type", "Unknown")
                    required = param.get("required", False)
                    prompt += f"- `{name}`: `{param_type}` (Required: {required})\n"
            else:
                prompt += "**No Parameters**\n"
                
    return prompt


# Step 3: Generate documentation using Llama
def generate_documentation_with_llama(prompt):
    # Load Llama model
    model_name = "Llama-2"  # Replace this with your Llama model name
    tokenizer = LlamaTokenizer.from_pretrained(model_name)
    model = LlamaForCausalLM.from_pretrained(model_name)

    # Encode the prompt text
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate the output
    outputs = model.generate(inputs["input_ids"], max_length=1000, num_return_sequences=1)

    # Decode the generated text
    documentation = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return documentation


# Step 4: Save the generated documentation to a Markdown file in the latest project folder
def save_documentation_to_file(documentation, project_folder):
    output_file_path = os.path.join(project_folder, "API_Documentation.md")
    with open(output_file_path, "w", encoding="utf-8") as md_file:
        md_file.write(documentation)
    print(f"✅ Documentation saved to {output_file_path}")


# Step 5: Find the latest fastapi_project folder
def find_latest_project_folder(base_dir):
    dirs = [d for d in os.listdir(base_dir) if d.startswith("fastapi_project_") and os.path.isdir(os.path.join(base_dir, d))]
    if not dirs:
        raise FileNotFoundError("❌ No project folder found.")
    dirs.sort(reverse=True)  # Sort in descending order to get the latest folder
    return os.path.join(base_dir, dirs[0])


# Main flow
def generate_api_docs(json_path, base_dir):
    # Load API data from the JSON file
    api_data = load_api_data(json_path)
    if api_data is None:
        return

    # Prepare the prompt for Llama
    prompt = prepare_prompt(api_data)

    # Generate documentation using Llama
    documentation = generate_documentation_with_llama(prompt)

    # Find the latest project folder
    project_folder = find_latest_project_folder(base_dir)

    # Save the generated documentation to the project folder
    save_documentation_to_file(documentation, project_folder)


# Define file paths
base_dir = os.getcwd()  # Get current working directory
json_file_path = os.path.join(base_dir, "extracted_data.json")

# Generate the API documentation
generate_api_docs(json_file_path, base_dir)


