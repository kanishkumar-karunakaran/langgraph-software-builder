from groq import Groq
import docx
import json
import os


# Set your Groq API Key here
GROQ_API_KEY = "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"

# Load Groq LLM Client
client = Groq(api_key=GROQ_API_KEY)

# Step 1: Parse .docx file and return combined cleaned text
def parse_srs_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

# Step 2: Call Groq LLaMA 3 to extract structured backend specs
def analyze_srs_text(srs_text):
    prompt = f"""
You are a senior backend architect. Analyze the given Software Requirements Specification (SRS) and extract the following technical elements in STRICT JSON format:


Return JSON like:
{{
  "api_endpoints": [
    {{
      "method": "GET",
      "path": "/users",
      "description": "Retrieve all users",
      "parameters": [{{ "name": "page", "type": "int", "required": false }}]
    }}
  ],
  "backend_logic": [
    "Users must be filtered by active status.",
    "If user role is admin, show all data."
  ],
  "database_schema": {{
    "tables": {{
      "users": {{
        "columns": {{
          "id": "integer",
          "name": "string",
          "email": "string",
          "created_at": "datetime"
        }},
        "primary_key": "id",
        "foreign_keys": []
      }}
    }}
  }},
  "authentication": {{
    "type": "JWT",
    "roles": ["admin", "user"],
    "rules": ["Admins can access all routes", "Users limited to /profile"]
  }}
}}


Be concise, structured, and correct. Avoid explanations. Only return the JSON.
----
SRS TEXT:
{srs_text}
"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content




# Step 4: Save the JSON response to a file
def save_to_json(data, file_path="extracted_data.json"):
    # Check if file exists and load its contents, otherwise create a new list
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)
    else:
        json_data = []


    # Append the new data
    json_data.append(data)


    # Write the updated data back to the JSON file
    with open(file_path, "w") as json_file:
        json.dump(json_data, json_file, indent=4)


# Step 5: Main runner
if __name__ == "__main__":
    file_path = "srs.docx"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
    else:
        srs_text = parse_srs_docx(file_path)
        result_str = analyze_srs_text(srs_text)


        # Debug: Print the raw response for inspection
        print("\nRaw response from Groq:\n", result_str)


        try:
            # Clean the response to ensure it's valid JSON format
            # Strip out extra text or error messages, leaving only the JSON part
            if result_str.startswith('{"') and result_str.endswith('}'):
                result_str = result_str.strip()
            else:
                # If the response contains non-JSON text, isolate the JSON part
                start_index = result_str.find("{")
                end_index = result_str.rfind("}") + 1
                result_str = result_str[start_index:end_index].strip()


            # Attempt to parse the cleaned string as JSON
            result_json = json.loads(result_str)


        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("Raw response from Groq:", result_str)
            result_json = {}


        print("\nExtracted System Requirements:\n")
        print(result_json)


        # Save to JSON file if successfully parsed
        if result_json:
            save_to_json(result_json)
