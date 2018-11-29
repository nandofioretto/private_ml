import numpy as np
from scipy.optimize import minimize


def noisevector(scale, length):
    """
        Computes a noise vector with density:
        v(b) = 1 / \alpha \exp(-\beta \| b \|)
        where \alpha is a normalizing constant. \beta is a function of epsilon_p.
    """

    r1 = np.random.normal(0, 1, length)
    # get the norm r1 (normally distributed)
    n1 = np.linalg.norm(r1, 2)
    # the norm of r2 is 1
    r2 = r1 / n1
    # Generate the norm of noise according to gamma distribution
    normn = np.random.gamma(length, 1 / scale, 1)
    # get the result noise vector
    res = r2 * normn
    return res

def lr(z):
    logr = np.log(1 + np.exp(-z))
    return logr


def lr_output_train(data, labels, epsilon, Lambda):
    L = len(labels)
    # length of a data point
    l = len(data[0])
    # chaudhuri2011differentially corollary 11, part 1
    scale = L * Lambda * epsilon / 2
    noise = noisevector(scale)
    # starting point with same length as any data point
    x0 = np.zeros(l)

    def obj_func(x):
        jfd = lr(labels[0] * np.dot(data[0], x))
        for i in range(1, L):
            jfd = jfd + lr(labels[i] * np.dot(data[i], x))
        f = (1 / L) * jfd + (1 / 2) * Lambda * (np.linalg.norm(x) ** 2)
        return f

    # minimization procedure
    f = minimize(obj_func, x0,
                 method='Nelder-Mead').x  # empirical risk minimization using scipy.optimize minimize function
    fpriv = f + noise
    return fpriv


def lr_objective_train(data, labels, epsilon, Lambda):
    # parameters in objective perturbation method
    c = 1 / 4  # chaudhuri2011differentially corollary 11, part 2
    L = len(labels)  # number of data points in the data set
    l = len(data[0])  # length of a data point
    x0 = np.zeros(l)  # starting point with same length as any data point
    Epsilonp = epsilon - 2 * np.log(1 + c / (Lambda * L))
    if Epsilonp > 0:
        Delta = 0
    else:
        Delta = c / (L * (np.exp(epsilon / 4) - 1)) - Lambda
        Epsilonp = epsilon / 2
    scale = Epsilonp / 2
    noise = noisevector(scale, l)

    def obj_func(x):
        jfd = lr(labels[0] * np.dot(data[0], x))
        for i in range(1, L):
            jfd = jfd + lr(labels[i] * np.dot(data[i], x))
        f = (1 / L) * jfd + (1 / 2) * Lambda * (np.linalg.norm(x) ** 2) + (1 / L) * np.dot(noise, x) + (
                    1 / 2) * Delta * (np.linalg.norm(x) ** 2)
        return f

    # minimization procedure
    fpriv = minimize(obj_func, x0,
                     method='Nelder-Mead').x  # empirical risk minimization using scipy.optimize minimize function
    return fpriv


def dp_logreg(data, labels, method='obj', epsilon=0.1, Lambda=0.01):
    '''
    This function provides a differentially-private estimate of the logistic regression classifier according to
    Sarwate et al. 2011, "Differentially Private Empirical Risk Minimization" paper.

    Input:

      data = data matrix, samples are in rows
      labels = labels of the data samples
      method = 'obj' (for objective perturbation) or 'out' (for output perturbation)
      epsilon = privacy parameter, default 1.0
      Lambda = regularization parameter

    Output:

      fpriv = (\epsilon)-differentially-private estimate of the svm classifier

    Example:

      >>> import numpy as np
      >>> n, d = 2, 5
      >>> X = np.random.normal(1.0, 1.0, (n,d));
      >>> Y = np.random.normal(-1.0, 1.0, (n,d));
      >>> labelX = 1.0 * np.ones(n);
      >>> labelY = -1.0 * np.ones(n);
      >>> data = np.vstack((X,Y));
      >>> labels = np.hstack((labelX,labelY));
      >>> fpriv = dp_logreg(data, labels, 'obj', 0.1, 0.01)
      >>> fpriv
      [ 1.45343603  6.59613827  3.39968451  0.56048388  0.69090816  1.7477234 -1.50873385 -2.06471724 -1.55284441  4.03065254]

    '''

    if epsilon < 0.0:
        print('ERROR: Epsilon should be positive.')
        return
    else:

        if method == 'obj':
            fpriv = lr_objective_train(data, labels, epsilon, Lambda)
        else:
            fpriv = lr_output_train(data, labels, epsilon, Lambda)

        return fpriv
