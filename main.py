from langgraph.graph import StateGraph
from nodes.analyse_node import node1_parse_srs
from nodes.setup_node import node2_generate_setup
from nodes.codegen_node import generate_code_from_requirements
from nodes.testcase_node import node_generate_tests
from nodes.downloadzip_node import download_project_zip

class FlowState(dict): pass

builder = StateGraph(FlowState)

builder.add_node("parse_srs", node1_parse_srs)
builder.add_node("generate_setup", node2_generate_setup)
builder.add_node("generate_tests", node_generate_tests)
builder.add_node("generate_code", generate_code_from_requirements)
builder.add_node("download_zip", download_project_zip)

builder.set_entry_point("parse_srs")
builder.add_edge("parse_srs", "generate_setup")
builder.add_edge("generate_setup", "generate_tests")
builder.add_edge("generate_tests", "generate_code")
builder.add_edge("generate_code", "download_zip") 

flow_app = builder.compile()

if __name__ == "__main__":
    inputs = {"srs_file": "srs.docx"}  
    
    while True:
        output = flow_app.invoke(inputs)  

        if output.get("tests_passed", False):  
            print("✅ All tests passed! Flow completed successfully.")
            break  
        else:
            print("⚠️ Tests failed. Regenerating code and retrying...")



