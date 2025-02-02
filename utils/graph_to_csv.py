"""

This script converts a JSON graph file into a CSV file with the following columns:
- repo: the repository url
- parent: the parent repository url (or 'ethereum' if it's a level 1 node)
- weight: the weight of the edge between the repository and its parent

The weight is simply calculated based on the number of nodes and edges in the graph:
- For every level 1 node, the weight is 0.5 / number of level 1 nodes 
- For every level 2 node, the weight is 0.5 / number of edge links from level 1 nodes to level 2 nodes

"""

import json
import csv
import argparse

def load_graph_data(input_path):
    with open(input_path, 'r') as f:
        return json.load(f)

def get_level_1_nodes(graph_data):
    return {
        node['id'] for node in graph_data['nodes'] 
        if node.get('level') == 1
    }

def calculate_weights(graph_data, level_1_nodes):
    level_1_count = len(level_1_nodes)
    level_2_count = sum(1 for link in graph_data['links'] 
                       if link['source'] in level_1_nodes)
    
    return {
        'level_1': 0.5 / level_1_count if level_1_count > 0 else 0,
        'level_2': 0.5 / level_2_count if level_2_count > 0 else 0
    }

def generate_csv_rows(graph_data, level_1_nodes, weights):
    csv_rows = []
    
    # Add level 1 nodes with "ethereum" as parent
    for node in graph_data['nodes']:
        if node.get('level') == 1:
            csv_rows.append({
                'repo': node['id'],
                'parent': 'ethereum',
                'weight': weights['level_1']
            })

    # Process links to get level 2 nodes
    for link in graph_data['links']:
        if link['source'] in level_1_nodes:
            csv_rows.append({
                'repo': link['target'],
                'parent': link['source'],
                'weight': weights['level_2']
            })
    
    return csv_rows

def write_csv(output_path, csv_rows):
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['repo', 'parent', 'weight'])
        writer.writeheader()
        writer.writerows(csv_rows)

def process_graph(input_path, output_path):
    graph_data = load_graph_data(input_path)
    level_1_nodes = get_level_1_nodes(graph_data)
    weights = calculate_weights(graph_data, level_1_nodes)
    csv_rows = generate_csv_rows(graph_data, level_1_nodes, weights)
    write_csv(output_path, csv_rows)

def main():
    parser = argparse.ArgumentParser(description='Convert graph JSON to CSV')
    parser.add_argument('--input_path', 
                       default='./graph/unweighted_graph_pruned_version.json',
                       help='Path to input JSON file')
    parser.add_argument('--output_path', 
                       default='./graph/pruned_repo_parent_weight_graph.csv',
                       help='Path to output CSV file')
    
    args = parser.parse_args()
    
    process_graph(args.input_path, args.output_path)

if __name__ == '__main__':
    main()
