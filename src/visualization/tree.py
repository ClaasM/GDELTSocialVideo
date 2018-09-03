import graphviz
from sklearn import tree

def decision_tree_graph(clf, feature_names, class_names=None):
    if class_names is None:
        class_names = ['True', 'False']
    dot_data = tree.export_graphviz(clf, out_file=None,
                                    feature_names=feature_names,
                                    class_names=class_names,
                                    filled=True, rounded=True,
                                    special_characters=True)
    return graphviz.Source(dot_data)
