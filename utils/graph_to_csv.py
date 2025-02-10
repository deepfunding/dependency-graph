"""
This script converts a JSON graph file into a CSV file with the following columns:
- repo: the repository url
- parent: the parent repository url (or 'ethereum' if it's a level 1 node)
- weight: the weight of the edge between the repository and its parent

It dynamically calculates weights for nodes in the following way:

1. Level 1 nodes:
   - All Level 1 repos' weights sum to 1 with respect to Ethereum
   - Each Level 1 repo also has a self-loop (pointing to itself):
     - If the repo has no children: self-loop weight = 1.0
     - If the repo has children: self-loop weight = 0.2, and remaining 0.8 is split evenly among children

2. Level 2 nodes:
   - For each Level 1 parent with children:
     - The parent's children share 0.8 of the weight evenly
     - For example, if a parent has 2 children, each gets weight 0.4

The output CSV is sorted in the following order:
1. All Level 1 -> ethereum links (sorted alphabetically by repo name)
2. For each Level 1 repo (sorted alphabetically):
   - First its self-loop
   - Then all its children (sorted alphabetically by repo name)
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

    # Calculate weights for level 2 nodes and self-loops
    level_2_weights = {}
    self_loop_weights = {}
    for level_1_node in level_1_nodes:
        children = level_2_parents[level_1_node]
        num_children = len(children)
        
        # If no children, self-loop gets full weight of 1.0
        if num_children == 0:
            self_loop_weights[level_1_node] = 1.0
        # If has children, self-loop gets 0.2 and remaining 0.8 split among children
        else:
            self_loop_weights[level_1_node] = 0.2
            weight_per_child = 0.8 / num_children
            level_2_weights[level_1_node] = {child: weight_per_child for child in children}

    return level_1_weights, level_2_weights, self_loop_weights

def generate_csv_rows(level_1_weights, level_2_weights, self_loop_weights):
    csv_rows = []

    # Level 1 weights (Seed nodes pointing to Ethereum)
    for repo, weight in level_1_weights.items():
        csv_rows.append({
            'repo': repo,
            'parent': 'ethereum',
            'weight': weight
        })
        # Add self-loop
        csv_rows.append({
            'repo': repo,
            'parent': repo,  # Self-loop
            'weight': self_loop_weights[repo]
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
    # Sort the rows:
    # 1. First all Level 1 -> ethereum links (sorted by repo name)
    # 2. Then for each Level 1 repo:
    #    - First its self-loop
    #    - Then all its children (sorted by repo name)
    
    def sort_key(row):
        if row['parent'] == 'ethereum':
            # Level 1 -> ethereum links come first
            return (0, row['repo'])
        elif row['repo'] == row['parent']:
            # Self-loops come second for each parent
            return (1, row['parent'], 0)
        else:
            # Children links come last, sorted by parent then child
            return (1, row['parent'], 1, row['repo'])
    
    sorted_rows = sorted(csv_rows, key=sort_key)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['repo', 'parent', 'weight'])
        writer.writeheader()
        writer.writerows(sorted_rows)

def process_graph(input_path, output_path):
    graph_data = load_graph_data(input_path)
    level_1_nodes, level_2_parents = get_level_nodes(graph_data)
    level_1_weights, level_2_weights, self_loop_weights = calculate_weights(level_1_nodes, level_2_parents)
    csv_rows = generate_csv_rows(level_1_weights, level_2_weights, self_loop_weights)
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