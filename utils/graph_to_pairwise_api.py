import json
import os

def process_graph(input_file, output_dir):
    # Load the JSON file
    with open(input_file, "r") as f:
        data = json.load(f)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output paths using the output directory
    output_categories = os.path.join(output_dir, "get1stLevelCategoryList.json")
    output_projects = os.path.join(output_dir, "getProjectsForCategory.json")
    output_metadata = os.path.join(output_dir, "getProjectMetadata.json")
    
    nodes = data["nodes"]

    # Initialize structures
    category_list = []
    projects_for_category = {}
    project_metadata = {}

    # Extract first and second-level nodes
    for node in nodes:
        # Store metadata for all nodes
        node_data = node.copy()
        if "level" in node_data:
            del node_data["level"]  # Remove the level attribute
        project_metadata[node["id"]] = node_data

        # Process category list and project mappings
        if node.get("level") == 1:
            category_id = node["id"]
            category_list.append(category_id)
            projects_for_category[category_id] = []

    # Map second-level nodes to their corresponding first-level nodes
    for edge in data.get("links", []):
        source = edge["source"]
        target = edge["target"]
        if source in projects_for_category:
            projects_for_category[source].append(target)

    # Save all three JSON files
    with open(output_categories, "w") as f:
        json.dump(category_list, f, indent=4)

    with open(output_projects, "w") as f:
        json.dump(projects_for_category, f, indent=4)

    with open(output_metadata, "w") as f:
        json.dump(project_metadata, f, indent=4)

    print(f"Output files generated in {output_dir}:\n1. {os.path.basename(output_categories)}\n2. {os.path.basename(output_projects)}\n3. {os.path.basename(output_metadata)}")

if __name__ == "__main__":
    input_file = input("Enter the path to the input JSON file: ")
    output_dir = input("Enter the directory path for output JSON files: ")
    
    process_graph(input_file, output_dir)