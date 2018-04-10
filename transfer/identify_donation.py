from argparse import ArgumentParser
import ast
import networkx as nx
import pickle


def to_ast_node(src):
    return ast.parse(src).body[0]
         
class DonationSlices(object):
    def __init__(self, graph, seed_columns, slices):
        self.graph = graph
        self.seed_columns = seed_columns
        self.slices = slices
        
    def __iter__(self):
        return iter(self.slices)
        
class FindExactColumnUse(ast.NodeVisitor):
    def __init__(self, columns):
        self.columns = set(columns)
        self.found = False
        
    def run(self, node):
        self.found = False
        self.visit(node)
        return self.found

    def visit_Str(self, node):
        if not self.found:
            self.found = node.s in self.columns
    
    def visit_Attribute(self, node):
        if not self.found:
            self.found = node.attr in self.columns

class ColumnAssignmentExtractor(object):
    def __init__(self, graph):
        self.graph = graph
    
    @staticmethod
    def is_assignment_to_target_columns(ast_node, target_columns):
        if not isinstance(ast_node, (ast.Assign, ast.AugAssign)):
            return False

        lhs = []
        if isinstance(ast_node, ast.Assign):
            lhs.extend(ast_node.targets)
        else:
            lhs.extend(ast_node)
    
        if isinstance(target_columns, str):
            target_columns = [target_columns]

        checker = FindExactColumnUse(target_columns)
        for lhs_node in lhs:
            if checker.run(lhs_node):
                return True

        return False

    def get_donation_slices(self, target_columns):
        seeds = []
        for node_id, node_data in self.graph.nodes(data=True):
            ast_node = to_ast_node(node_data['src'])
            if self.is_assignment_to_target_columns(ast_node, target_columns):
                seeds.append(node_id)

        slices = []
        reversed_graph = self.graph.reverse(copy=False)
        for node_id in seeds:
            slice_nodes = nx.dfs_tree(reversed_graph, node_id)
            _slice = graph.subgraph(slice_nodes)
            slices.append(_slice)
        return DonationSlices(graph, target_columns, slices)
        

class Trimmer(object):
    pass
# trim slice and identify function arguments   

class SliceLifter(object):
    pass

# lift slice to function
# return code to user

def main(args):
    graph_file = args.graph_file
    slices_file = args.output_file
    target_columns = args.targets
    
    with open(graph_file, 'rb') as f:
        graph = pickle.load(f)
    extractor = ColumnAssignmentExtractor(graph)
    donations = extractor.get_donation_slices(target_columns)

    with open(slices_file, 'wb') as f:
        pickle.dump(donations, f)


if __name__ == '__main__':
    parser = ArgumentParser(description='Extract candidate donation slices')
    parser.add_argument('graph_file', type=str, help='File path to pickled networkx graph')
    parser.add_arugment('output_file', type=str, help='File path to pickle output slices')
    args = parser.parse_args()
    try:
        main(args)
    except:
        import pdb
        pdb.post_mortem()
    
    



