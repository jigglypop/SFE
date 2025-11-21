import numpy as np

def density_matrix_from_statevector(psi):
    return np.outer(psi, psi.conj())

def fidelity(rho1, rho2):
    rho1 = np.array(rho1, dtype=complex)
    rho2 = np.array(rho2, dtype=complex)
    w1, v1 = np.linalg.eigh(rho1)
    w1 = np.clip(w1, 0.0, None)
    sqrt_rho1 = (v1 * np.sqrt(w1)) @ v1.conj().T
    M = sqrt_rho1 @ rho2 @ sqrt_rho1
    wM = np.linalg.eigvalsh(M)
    wM = np.clip(wM, 0.0, None)
    return float(np.real(np.sum(np.sqrt(wM)) ** 2))

def purity(rho):
    return np.real(np.trace(rho @ rho))

def entropy(rho):
    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = eigenvalues[eigenvalues > 1e-15]
    return -np.sum(eigenvalues * np.log2(eigenvalues))

def pauli_expectation(rho, pauli_matrix):
    return np.real(np.trace(rho @ pauli_matrix))

def format_results(results_dict, precision=4):
    formatted = {}
    for key, value in results_dict.items():
        if isinstance(value, (int, float, np.number)):
            if abs(value) > 1e3 or abs(value) < 1e-3:
                formatted[key] = f"{value:.{precision}e}"
            else:
                formatted[key] = f"{value:.{precision}f}"
        else:
            formatted[key] = value
    return formatted

def print_results_table(results_dict, title=None):
    if title:
        print("=" * 60)
        print(title)
        print("=" * 60)
    
    formatted = format_results(results_dict)
    max_key_len = max(len(str(k)) for k in formatted.keys())
    
    for key, value in formatted.items():
        print(f"  {key:<{max_key_len}} : {value}")
    
    if title:
        print("=" * 60)

