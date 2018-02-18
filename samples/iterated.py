# -*- coding: utf-8 -*-

# This is a sample script. It derives DependencyBuilder and
# implements a filtre function which only lets those trees
# pass which contain 'give' with a 'to'-pobj child.
#
# This is a more elegant version using a tree iterator.


from SeaCOW import Query, ConcordanceWriter, DependencyBuilder
from anytree import Node, RenderTree, PreOrderIter

class IterativelyFiltredDependencyBuilder(DependencyBuilder):

  # Implemented filtre function.
  def filtre(self, tree, line):
    return(len([node.lemma for node in PreOrderIter(tree[0],
      filter_ = lambda n:
        hasattr(n, 'relation') and n.relation == u'pobj' and n.parent.lemma == u'to' and n.parent.parent.lemma == u'give')])>0)
