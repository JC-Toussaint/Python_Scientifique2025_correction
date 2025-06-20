import scipy
from scipy import sparse

N=100
A=sparse.rand(N, N, density=0.1, random_state=123) 
A=A+A.T # symmétrisation

# Recette pour rendre une matrice definie positive
D=A.diagonal() 		# partie diagonale
A=A-sparse.diags(D)	# suppression
S=np.abs(A).sum(axis=1)	# somme des v.a. des termes de chaque ligne
D=S.flatten().tolist()	# Applatissage et conversion vers liste

W=sparse.diags(D[0])
A=A+W

n=2
vals, vecs = sparse.linalg.eigsh(A, k=n, which='SM')
print(vals)
print(vecs[:, 0])
A*vecs[:, 0]-vals[0]*vecs[:, 0]

