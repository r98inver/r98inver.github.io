class TreeNode:
	def __init__(self, label):
		self.label = label
		self.children = []

	def add_child(self, child_node):
		self.children.append(child_node)

	def is_leaf(self):
		return self.children == []

	def __eq__(self, other):
		# Nodes are identified by labels
		return self.label == other.label

def compute_names(v, names={}):
	"""
	Algorithm 4: ComputeNames
	"""
	if v.is_leaf():
		# The name of each leaf is 10
		names[v.label] = "10"
		return names

	# Compute a sorted list of all the child names
	temp = []
	for u in v.children:
		names = compute_names(u, names)
		temp.append(names[u.label])
	temp.sort()

	# Compute the node name
	node_name = '1' + ''.join(temp) + '0'
	names[v.label] = node_name

	return names

def compute_path_names(r):
	"""
	Algorithm 1: ComputePathNames
	"""
	names = compute_names(r)
	h = lambda x: x # Add a hash function to improve efficiency

	path_names = { r.label:h(names[r.label]) }

	S = [(v, r) for v in r.children] # (node, parent)

	while S != []:
		v, u = S.pop(0)
		can_path_name = names[v.label] + ';' + path_names[u.label]
		path_names[v.label] = h(can_path_name)
		for w in v.children:
			S.append((w, v)) # (node, parent)

	return path_names

def SDSP_to_tree(root, SDSP):
	"""
	SDSP is a dictionary from nx.single_source_shortest_path(G, root)
	in the form { node : [SP from root to node] }
	"""
	root = TreeNode(str(root))

	for path_dest in SDSP:
		path = SDSP[path_dest]
		assert str(path[0]) == root.label, path
		curr_node = root

		for i in range(1, len(path)):
			next_label = path[i]
			next_node = TreeNode(str(next_label))
			if next_node in curr_node.children:
				# Same label but different children:
				# we pick the one already in the tree
				for cd in curr_node.children:
					if cd == next_node:
						next_node = cd 
						break
			else:
				curr_node.add_child(next_node)

			curr_node = next_node

		assert curr_node.label == str(path_dest)

	return root