# Adapted from https://colab.research.google.com/github/mathcoding/opt4ds/blob/master/notebooks/ColorTransfer.ipynb#scrollTo=01OTTXi0BhUK

import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist

def load_image(filename):
	return plt.imread(filename).astype(np.float64) / 255

def show_image(img):
	fig, ax = plt.subplots()
	
	plt.imshow(img)
	
	ax.autoscale()
	ax.set_aspect('equal', 'box')
	plt.axis('off')
	plt.show()

def point_samples(img, n_samples=100):
	r, c, h = img.shape 
	img = img.reshape(r*c, 3)
	s = np.random.randint(0, r*c, n_samples)
	return img[s]

def display_cloud(img, n_samples=100):
	r, c, h = img.shape 
	
	img = img.reshape(r*c, 3)
	
	s = np.random.randint(0, r*c, n_samples)
	
	fig = plt.figure()
	ax = fig.add_subplot(projection='3d')
	
	plt.scatter(x=img[s,0], y=img[s,1], zs=img[s,2], s=10, c=img[s])
	plt.show()

def D(a,b):
	return np.linalg.norm(a-b)**2

def closest_rgb(A, B):
	return np.argmin(cdist(A, B), axis=1)

def OT(H1, H2):
	n = len(H1)

	model = gp.Model('images')

	# Define variables
	m_vars = model.addVars(n, n, vtype=GRB.BINARY, name='ot')

	# Mapping is one to one
	model.addConstrs((m_vars.sum(i, '*') == 1 for i in range(n)), name='R');
	model.addConstrs((m_vars.sum('*', j) == 1 for j in range(n)), name='C');

	# Matching cost to optimize
	model.setObjective(
		gp.quicksum(
			m_vars[i, j]*D(H1[i], H2[j]) for i in range(n) for j in range(n)
		), 
		GRB.MINIMIZE)

	model.optimize()
	
	color_map = []
	sol = model.getAttr('X', m_vars)
	for i in range(n):
		for j in range(n):
			if sol[i, j] > 0.5:
				color_map.append(j)

	return color_map


if __name__ == "__main__":
	img1 = load_image('gaudi1.jpg')  # Base image
	img2 = load_image('colori.jpeg') # Color image

	# print(img1.shape)
	# print(img2.shape)    
	
	# show_image(img2)
	# display_cloud(img1, 500)
	
	H1 = point_samples(img1, 200)
	H2 = point_samples(img2, 200)

	color_map = OT(H1, H2)
	
	
	r,c,_ = img1.shape
	C = img1.reshape(r*c, 3)
	
	Y = closest_rgb(C, H1)
	
	H4 = np.array([ H2[color_map[i]] for i in Y] )
	H5 = H4.reshape(r, c, 3)
	
	show_image(H5)



