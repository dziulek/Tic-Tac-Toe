import numpy as np
from src.game import TicTacGame
from src.agent import Node
from typing import Dict, List

def prune_tree(tree: Dict[str, Node], node: TicTacGame):

    if node not in tree.keys():
        return tree

    new_tree: Dict[str, Node] = {}

    stack: List[str] = []

    stack.append(node.hash())
    while len(stack) > 0:
        curr_node = stack.pop()
        new_tree[curr_node] = tree[curr_node]

        for action, _hash in tree[curr_node].ea:
            stack.append(_hash)

    return new_tree

    

def find_root(tree: Dict[str, Node], node: TicTacGame):

    tmp = node.clone()

    while tree[node.hash()].parent is not None:

        tmp = tree[node.hash()].parent

    return tmp