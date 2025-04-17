from langgraph.graph import StateGraph
from nodes.analyse_node import node1_parse_srs
from nodes.setup_node import node2_generate_setup
from nodes.codegen_node import node3_generate_code

class FlowState(dict): pass

builder = StateGraph(FlowState)

builder.add_node("parse_srs", node1_parse_srs)
builder.add_node("generate_setup", node2_generate_setup)
builder.add_node("generate_code", node3_generate_code)

# Step 3: Connect them
builder.set_entry_point("parse_srs")
builder.add_edge("parse_srs", "generate_setup")
builder.add_edge("generate_setup", "generate_code")

# Step 4: Compile
flow_app = builder.compile()

# Step 5: Run
if __name__ == "__main__":
    inputs = {"srs_file": "isrs.docx"}
    output = flow_app.invoke(inputs)


