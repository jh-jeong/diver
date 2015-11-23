import numpy as np
from scipy.sparse import csc_matrix,dok_matrix
from scipy.sparse import linalg as linalg_s
from scipy import linalg

class MatrixCompletion:
    """ A general class to represent a matrix completion problem

    Data members 
    ==================== 
    M:= data matrix (numpy array).
    X:= optimized data matrix (numpy array)
    out_info:= output information for the optimization (list) 


    Class methods
    ====================
    complete_it():= method to complete the matrix
    get_optimized_matrix():= method to get the solution to the problem
    get_matrix():= method to get the original matrix
    get_out():= method to get extra information on the optimization (iter
    number, convergence, objective function)

    """
    def __init__(self, X,*args, **kwargs):
        """ Constructor for the problem instance

            Inputs:
             1) X: known data matrix. Numpy array with np.nan on the unknow entries. 
                example: 
                    X = np.random.randn(5, 5)
                    X[1][3] = np.nan
                    X[0][0] = np.nan
                    X[4][4] = np.nan

        """
        # Initialization of the members
        self._M = X
        self._X = np.array(X, copy = True) #Initialize with ini data matrix
        self._out_info = []

    def get_optimized_matrix(self):
        """ Getter function to return the optimized matrix X 

            Ouput:
             1) Optimized matrix
        """
        return self._X

    def get_matrix(self):
        """ Getter function that returns the original matrix M

            Output:
            1) Original matrix M
        """
        return self._M

    def get_out(self):
        """ Getter function to return the output information 
            of the optimization

            Output:
             1) List of length 2: number of iterations and relative residual

        """
        return self._out_info


    def _ASD(self, M, r = None, reltol=1e-5, maxiter=5000):
        """
        Alternating Steepest Descent (ASD)
        Taken from Low rank matrix completion by alternating steepest descent methods
        Jared Tanner and Ke Wei
        SIAM J. IMAGING SCIENCES (2014)
        
        We have a matrix M with incomplete entries,
        and want to estimate the full matrix
        
        Solves the following relaxation of the problem:
        minimize_{X,Y} \frac{1}{2} ||P_{\Omega}(Z^0) - P_\{Omega}(XY)||_F^2
        Where \Omega represents the set of m observed entries of the matrix M
        and P_{\Omega}() is an operator that represents the observed data. 
        
        Inputs:
         M := Incomplete matrix, with NaN on the unknown matrix
         r := hypothesized rank of the matrix
        
        Usage:
         Just call the function _ASD(M)
        """
    
        # Get shape and Omega
        m, n = M.shape
        if r == None:
            r = min(m-1, n-1, 50)
    
        # Set relative error
        I, J = [], []
        M_list = []
        for i, j in M.keys():
            I.append(i)
            J.append(j)
            M_list.append(M[i,j])
        M_list = np.array(M_list)
        Omega = [I,J]
        frob_norm_data = linalg_s.norm(M)
        relres = reltol * frob_norm_data
    
        # Initialize
        M_omega = M.tocsc()
        U, s, V = linalg_s.svds(M_omega, r)
        S = np.diag(s)
        X = np.dot(U, S)
        Y = V
        itres = np.zeros((maxiter+1, 1))
    
        XY = np.dot(X, Y)
        diff_on_omega = M_list - XY[Omega]
        res = linalg.norm(diff_on_omega)
        iter_c = 0
        itres[iter_c] = res/frob_norm_data 

        while iter_c < maxiter and res >= relres:
            
            # Gradient for X
            diff_on_omega_matrix = np.zeros((m,n))
            diff_on_omega_matrix[Omega] = diff_on_omega
            grad_X = np.dot(diff_on_omega_matrix, np.transpose(Y))
            
            # Stepsize for X
            delta_XY = np.dot(grad_X, Y)
            tx = linalg.norm(grad_X,'fro')**2/linalg.norm(delta_XY)**2
        
            # Update X
            X = X + tx*grad_X;
            diff_on_omega = diff_on_omega-tx*delta_XY[Omega]
        
            # Gradient for Y
            diff_on_omega_matrix = np.zeros((m,n))
            diff_on_omega_matrix[Omega] = diff_on_omega
            Xt = np.transpose(X)
            grad_Y = np.dot(Xt, diff_on_omega_matrix)
        
            # Stepsize for Y
            delta_XY = np.dot(X, grad_Y)
            ty = linalg.norm(grad_Y,'fro')**2/linalg.norm(delta_XY)**2
        
            # Update Y
            Y = Y + ty*grad_Y
            diff_on_omega = diff_on_omega-ty*delta_XY[Omega]
            
            res = linalg.norm(diff_on_omega)
            iter_c = iter_c + 1
            itres[iter_c] = res/frob_norm_data
    
        M_out = np.dot(X, Y)
    
        out_info = [iter_c, itres]
    
        return M_out, out_info    

    def _sASD(self, M, r = None, reltol=1e-5, maxiter=10000):
        """
        Scaled Alternating Steepest Descent (ScaledASD)
        Taken from:
        Low rank matrix completion by alternating steepest descent methods
        Jared Tanner and Ke Wei
        SIAM J. IMAGING SCIENCES (2014)
        
        We have a matrix M with incomplete entries,
        and want to estimate the full matrix
        
        Solves the following relaxation of the problem:
        minimize_{X,Y} \frac{1}{2} ||P_{\Omega}(Z^0) - P_\{Omega}(XY)||_F^2
        Where \Omega represents the set of m observed entries of the matrix M
        and P_{\Omega}() is an operator that represents the observed data. 
        
        Inputs:
         M := Incomplete matrix, with NaN on the unknown matrix
         r := hypothesized rank of the matrix
        
        Usage:
         Just call the function _sASD(M)
        """
    
    
        # Get shape and Omega
        m, n = M.shape
        if r == None:
            r = min(m-1, n-1, 50)
    
        # Set relative error
        I, J = [], []
        M_list = []
        for i, j in M.keys():
            I.append(i)
            J.append(j)
            M_list.append(M[i,j])
        M_list = np.array(M_list)
        
        print(M_list)
        Omega = [I,J]
        frob_norm_data = linalg_s.norm(M)
        relres = reltol * frob_norm_data
    
        # Initialize
        identity = np.identity(r);
        M_omega = M.tocsc()
        U, s, V = linalg_s.svds(M_omega, r)
        S = np.diag(s)
        X = np.dot(U, S)
        Y = V
        itres = np.zeros((maxiter+1, 1)) 
    
        XY = np.dot(X, Y)
        diff_on_omega = M_list - XY[Omega]
        print(diff_on_omega)
        res = linalg.norm(diff_on_omega)
        iter_c = 0
        itres[iter_c] = res/frob_norm_data

        while iter_c < maxiter and res >= relres:
    
            # Gradient for X
            diff_on_omega_matrix = np.zeros((m,n))
            diff_on_omega_matrix[Omega] = diff_on_omega
            grad_X = np.dot(diff_on_omega_matrix, np.transpose(Y))
    
            # Scaled gradient
            scale = linalg.solve(np.dot(Y, np.transpose(Y)), identity)
            dx = np.dot(grad_X, scale) 
    
            delta_XY = np.dot(dx, Y)
            tx = np.trace(np.dot(np.transpose(dx),grad_X))/linalg.norm(delta_XY[Omega])**2
    
            # Update X
            X = X + tx*dx
            diff_on_omega = diff_on_omega-tx*delta_XY[Omega]
    
            # Gradient for Y
            diff_on_omega_matrix = np.zeros((m,n))
            diff_on_omega_matrix[Omega] = diff_on_omega
            Xt = np.transpose(X)
            grad_Y = np.dot(Xt, diff_on_omega_matrix)
    
            # Scaled gradient
            scale = linalg.solve(np.dot(Xt, X), identity)
            dy = np.dot(scale, grad_Y) 
    
            # Stepsize for Y
            delta_XY = np.dot(X, dy)
            ty = np.trace(np.dot(dy,np.transpose(grad_Y)))/linalg.norm(delta_XY[Omega])**2
    
            # Update Y
            Y = Y + ty*dy
            diff_on_omega = diff_on_omega-ty*delta_XY[Omega]
    
            # Update iteration information
            res = linalg.norm(diff_on_omega)
            iter_c = iter_c + 1
            itres[iter_c] = res/frob_norm_data 
    
        M_out = np.dot(X, Y)
    
        out_info = [iter_c, itres]
    
        return M_out, out_info

    def complete_it(self, algo_name, r = None, reltol=1e-5, maxiter=5000):
 
        """ Function to solve the optimization with the choosen algorithm 

            Input:
             1) algo_name: Algorithm name (ASD, sASD, ect)
             2) r: rank of the matrix if performing alternating algorithm
        """
        if algo_name == "ASD":
            self._X, self._out_info = self._ASD(self._M, r, reltol, maxiter)
        elif algo_name == "sASD":
            self._X, self._out_info = self._sASD(self._M, r, reltol, maxiter)
        else:
            raise NameError("Algorithm name not recognized")
