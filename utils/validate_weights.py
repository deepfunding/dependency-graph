from collections import defaultdict
import networkx as nx
from typing import Dict


def validate_weights(graph: nx.Graph) -> Dict[str, float]:
    """
    Validate the weights of the edges in the graph by checking if any source's total weight exceeds 1.0.
    
    Args:
        graph: A NetworkX graph containing weighted edges
        
    Returns:
        A dictionary mapping source nodes to their total outgoing weights
        
    Examples:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', weight=0.5)
        >>> G.add_edge('A', 'C', weight=0.6)
        >>> weights = validate_weights(G)
        >>> weights['A']  # Will print warning as total weight is 1.1
        1.1
    """
    try:
        source_weights = defaultdict(float)
        
        # Sum up weights for each source node
        for u, v, data in graph.edges(data=True):
            weight = data.get("weight", 0)
            source_weights[u] += weight

        # Check for invalid weights
        invalid_sources = {
            source: total 
            for source, total in source_weights.items() 
            if total > 1.0
        }
        
        if invalid_sources:
            print("Warning: The following sources exceed the weight limit of 1.0:")
            for source, total in invalid_sources.items():
                print(f"Source: {source}, Total Weight: {total}")
        
        return dict(source_weights)
    
    except Exception as e:
        raise RuntimeError(f"Error validating weights: {str(e)}") from e
