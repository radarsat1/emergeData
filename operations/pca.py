#!/usr/bin/env python

__all__ = ['get_pca_transform']

from numpy import mean,cov,double,cumsum,dot,linalg,array,rank
from pylab import *

def princomp(A,numpc=1):
    """PCA using linalg.eig, from http://glowingpython.blogspot.it/2011/07/pca-and-image-compression-with-numpy.html"""
    # computing eigenvalues and eigenvectors of covariance matrix
    M = (A-mean(A.T,axis=1)).T # subtract the mean (along columns)
    [latent,coeff] = linalg.eig(cov(M))
    p = size(coeff,axis=1)
    idx = argsort(latent) # sorting the eigenvalues
    idx = idx[::-1]       # in ascending order
    # sorting eigenvectors according to the sorted eigenvalues
    coeff = coeff[:,idx]
    latent = latent[idx] # sorting eigenvalues
    if numpc < p or numpc >= 0:
        coeff = coeff[:,range(numpc)] # cutting some PCs
    score = dot(coeff.T,M) # projection of the data in the new space
    return coeff,score,latent

# In practice, linalg.eig is too slow on large vectors such as
# autocorrelation, so we use matplitlib.mlab.prepca, which uses SVD
# for eigenvalue decomposition.
from matplotlib.mlab import prepca

def get_pca_transform(blocks, numpcs=2, feature='axes_correlation'):
    # Put all blocks together into one big array
    vectors = concatenate([b[feature] for b in blocks
                           if b[feature].shape!=(0,)]).T
    # coeff, score, latent = princomp(vectors, numpcs)
    Pcomponents, Trans, fracVar = prepca(vectors)
    return Trans

# Example of how to use princomp, from
# http://glowingpython.blogspot.it/2011/07/pca-and-image-compression-with-numpy.html
if __name__=="__main__":
    A = array([ [2.4,0.7,2.9,2.2,3.0,2.7,1.6,1.1,1.6,0.9],
                [2.5,0.5,2.2,1.9,3.1,2.3,2,1,1.5,1.1] ])
    
    coeff, score, latent = princomp(A.T, 2)
    
    figure()
    subplot(121)
    # every eigenvector describe the direction
    # of a principal component.
    m = mean(A,axis=1)
    plot([0, -coeff[0,0]*2]+m[0], [0, -coeff[0,1]*2]+m[1],'--k')
    plot([0, coeff[1,0]*2]+m[0], [0, coeff[1,1]*2]+m[1],'--k')
    plot(A[0,:],A[1,:],'ob') # the data
    axis('equal')
    subplot(122)
    # new data
    plot(score[0,:],score[1,:],'*g')
    axis('equal')
    show()
