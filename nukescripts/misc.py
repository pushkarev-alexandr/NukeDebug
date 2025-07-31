import nuke

def clear_selection_recursive(group = nuke.root()):
  """Sets all nodes to unselected, including in child groups."""
  for n in group.selectedNodes():
    n.setSelected(False)
  groups = [i for i in group.nodes() if i.Class() == 'Group']
  for i in groups:
    clear_selection_recursive(i)
