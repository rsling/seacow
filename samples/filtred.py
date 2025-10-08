# -*- coding: utf-8 -*-

# This is a sample script. It derives DependencyBuilder and
# implements a filtre function which only lets those trees
# pass which contain 'give' with a 'to'-pobj child.
#
# This is a slightly clumsy version without a tree iterator.

from SeaCOW import Query, ConcordanceWriter, DependencyBuilder
from anytree import Node, RenderTree, findall, findall_by_attr, AsciiStyle

class FiltredDependencyBuilder(DependencyBuilder):

  # Implemented filtre function.
  def filtre(self, tree, line):

    # Don't use very complex trees because they are usually misanalysed.
    if len(tree) > 30:
      return False

    # Find the 'give' nodes.
    gives = findall_by_attr(tree[0], value = 'give', name = 'lemma')

    # For simplicity's sake, only use trees with one give.
    if len(gives) > 1:
      return False

    # Search 'pobj' nodes below 'give' node
    pobjs = findall_by_attr(gives[0], value = 'pobj', name = 'relation', maxlevel = 3)

    if len(pobjs) < 1:
      return False

    # Finally, check whether the parent of any of the pobj nodes is 'to'.
    return(any([True if x.parent.lemma == 'to' else False for x in pobjs]))
