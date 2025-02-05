"""

This script converts a JSON graph file into a CSV file with the following columns:
- repo: the repository url
- parent: the parent repository url (or 'ethereum' if it's a level 1 node)
- weight: the weight of the edge between the repository and its parent

It dynamically calculates the weights for Level 1 and Level 2 nodes, ensuring that they are evenly distributed within their respective levels:

1.	Each Level 1 repo’s weights sum to 1 with respect to Ethereum.
2.	Each Level 2 repo’s weights sum to 1 with respect to its parent Level 1 repo.

"""

import json
import csv
import argparse
from collections import defaultdict

def load_graph_data(input_path):
    with open(input_path, 'r') as f:
        return json.load(f)

def get_level_nodes(graph_data):
    level_1_nodes = set()
    level_2_parents = defaultdict(set)

    for node in graph_data['nodes']:
        if node.get('level') == 1:
            level_1_nodes.add(node['id'])

    for link in graph_data['links']:
        if link['source'] in level_1_nodes:
            level_2_parents[link['source']].add(link['target'])

    return level_1_nodes, level_2_parents

def calculate_weights(level_1_nodes, level_2_parents):
    level_1_weights = {node: 1.0 / len(level_1_nodes) for node in level_1_nodes} if level_1_nodes else {}

    level_2_weights = {}
    for parent, children in level_2_parents.items():
        num_children = len(children)
        if num_children > 0:
            level_2_weights[parent] = {child: 1.0 / num_children for child in children}

    return level_1_weights, level_2_weights

def generate_csv_rows(level_1_weights, level_2_weights):
    csv_rows = []

    # Level 1 weights (Seed nodes pointing to Ethereum)
    for repo, weight in level_1_weights.items():
        csv_rows.append({
            'repo': repo,
            'parent': 'ethereum',
            'weight': weight
        })

    # Level 2 weights (Dependencies pointing to their parent Level 1 repo)
    for parent, children_weights in level_2_weights.items():
        for repo, weight in children_weights.items():
            csv_rows.append({
                'repo': repo,
                'parent': parent,
                'weight': weight
            })

    return csv_rows

def write_csv(output_path, csv_rows):
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['repo', 'parent', 'weight'])
        writer.writeheader()
        writer.writerows(csv_rows)

def process_graph(input_path, output_path):
    graph_data = load_graph_data(input_path)
    level_1_nodes, level_2_parents = get_level_nodes(graph_data)
    level_1_weights, level_2_weights = calculate_weights(level_1_nodes, level_2_parents)
    csv_rows = generate_csv_rows(level_1_weights, level_2_weights)
    write_csv(output_path, csv_rows)

def main():
    parser = argparse.ArgumentParser(description='Convert graph JSON to CSV with hierarchical weighting')
    parser.add_argument('--input_path', 
                        default='./graph/unweighted_graph.json',
                        help='Path to input JSON file')
    parser.add_argument('--output_path', 
                        default='./graph/repo_parent_weight_graph.csv',
                        help='Path to output CSV file')
    
    args = parser.parse_args()
    
    process_graph(args.input_path, args.output_path)

if __name__ == '__main__':
    main()