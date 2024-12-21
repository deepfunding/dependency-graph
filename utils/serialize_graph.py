import networkx as nx
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Union
from datetime import date, datetime


def to_native(obj: Any) -> Union[Dict, List, int, float, bool, None, str, Any]:
    """
    Convert numpy and pandas data types to native Python types.
    
    Args:
        obj: Any object that needs to be converted to native Python types
        
    Returns:
        The input object converted to native Python types
        
    Examples:
        >>> to_native(np.int64(5))
        5
        >>> to_native({'a': np.float64(1.0)})
        {'a': 1.0}
    """
    if isinstance(obj, dict):
        return {k: to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_native(v) for v in obj]
    elif isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (pd.Timestamp, datetime, date)):
        return obj.isoformat()
    elif pd.isna(obj):
        return None
    else:
        return obj


def convert_graph_to_serializable(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Convert a NetworkX graph with numpy/pandas data types to a serializable format.
    
    Args:
        graph: A NetworkX directed graph potentially containing numpy/pandas data types
        
    Returns:
        A new NetworkX directed graph with all data converted to native Python types
        
    Raises:
        TypeError: If the input is not a NetworkX DiGraph
        ValueError: If the graph is empty
        
    Examples:
        >>> G = nx.DiGraph()
        >>> G.add_node(1, weight=np.float64(2.0))
        >>> G_serial = convert_graph_to_serializable(G)
        >>> type(G_serial.nodes[1]['weight'])
        <class 'float'>
    """
    if not isinstance(graph, nx.DiGraph):
        raise TypeError("Input must be a NetworkX DiGraph")
    
    if len(graph) == 0:
        raise ValueError("Input graph is empty")
    
    try:
        G_serializable = nx.DiGraph()
        
        # Convert node data
        for node, data in graph.nodes(data=True):
            G_serializable.add_node(node, **to_native(data))
        
        # Convert edge data
        for u, v, data in graph.edges(data=True):
            G_serializable.add_edge(u, v, **to_native(data))
        
        return G_serializable
    
    except Exception as e:
        raise RuntimeError(f"Error converting graph to serializable format: {str(e)}") from e
                                         