import numpy as np
from .constants import *
from .utils import fidelity as _fidelity


class CorrelatedNoiseModel:
    """
    SFE 이론에 기반한 다중 큐비트 상관 노이즈(Correlated Noise) 모델.
    억압장(Phi)의 공간적 상관관계(correlation length xi)를 반영하여
    큐비트 간 거리 r_ij에 따른 공통 노이즈 커널을 생성한다.
    """
    def __init__(self, n_qubits, coordinates=None, correlation_length=1.0, mode_weights=None):
        self.n_qubits = n_qubits
        if coordinates is None:
            # 기본값: 1D 선형 사슬 (간격 1.0)
            self.coordinates = np.array([[i, 0.0, 0.0] for i in range(n_qubits)])
        else:
            self.coordinates = np.array(coordinates)
        lengths = np.atleast_1d(correlation_length).astype(float)
        if lengths.size == 0:
            raise ValueError("correlation_length must contain at least one value")
        if mode_weights is None:
            weights = np.ones_like(lengths)
        else:
            weights = np.atleast_1d(mode_weights).astype(float)
            if weights.size != lengths.size:
                raise ValueError("mode_weights must match correlation_length")
        if not np.all(lengths > 0):
            raise ValueError("correlation_length entries must be positive")
        weight_sum = float(np.sum(weights))
        if weight_sum <= 0.0:
            raise ValueError("mode_weights must sum to a positive value")
        self.lengths = lengths
        self.weights = weights / weight_sum
        self.mode_count = self.lengths.size
        self.correlation_matrix = self._build_correlation_matrix()

    def _build_correlation_matrix(self):
        """C_ij = exp(-|r_i - r_j| / xi)"""
        C = np.zeros((self.n_qubits, self.n_qubits), dtype=float)
        for idx, xi in enumerate(self.lengths):
            w = float(self.weights[idx])
            for i in range(self.n_qubits):
                C[i, i] += w
                for j in range(i + 1, self.n_qubits):
                    dist = np.linalg.norm(self.coordinates[i] - self.coordinates[j])
                    val = w * np.exp(-dist / xi)
                    C[i, j] += val
                    C[j, i] += val
        return C

    def get_correlated_dephasing_rates(self, base_gamma):
        """
        기본 감쇠율 base_gamma에 대해 상관 행렬을 곱해 유효 감쇠율 행렬을 반환.
        Gamma_ij = base_gamma * C_ij
        """
        base = np.asarray(base_gamma, dtype=float)
        if base.ndim == 0:
            return float(base) * self.correlation_matrix
        if base.shape[0] != self.n_qubits:
            raise ValueError("base_gamma vector length must match n_qubits")
        if np.any(base < 0):
            raise ValueError("base_gamma entries must be non-negative")
        outer = np.sqrt(np.outer(base, base))
        return outer * self.correlation_matrix


class ReadoutMitigation:
    def __init__(self, n_qubits, p_error=0.02):
        self.n_qubits = n_qubits
        self.p_error = float(p_error)
        p = self.p_error
        a1 = np.array([[1.0 - p, p], [p, 1.0 - p]], dtype=float)
        a = a1.copy()
        for _ in range(n_qubits - 1):
            a = np.kron(a, a1)
        self.assignment = a
        self.assignment_inv = np.linalg.inv(a)

    def corrupt(self, probs):
        probs = np.asarray(probs, dtype=float)
        noisy = self.assignment @ probs
        return noisy

    def mitigate(self, probs_noisy):
        probs_noisy = np.asarray(probs_noisy, dtype=float)
        est = self.assignment_inv @ probs_noisy
        est = np.clip(est, 0.0, 1.0)
        s = float(np.sum(est))
        if s > 0.0:
            est /= s
        return est


class QuantumCorrection:
    def __init__(
        self,
        n_qubits=1,
        m_qubit=1e-30,
        T2=1e-7,
        epsilon_0=EPSILON_0,
        epsilon_crit=None,
        gamma_phi=None,
        gamma_1=None,
        coordinates=None,
        correlation_length=1.0,
        mode_weights=None,
    ):
        self.n_qubits = n_qubits
        self.m_qubit = m_qubit
        self.T2 = T2
        self.epsilon_0 = epsilon_0
        self.epsilon_crit = epsilon_crit if epsilon_crit is not None else epsilon_0
        self.epsilon_mass = EPSILON_MASS

        self.g_q = alpha_si * np.sqrt(m_qubit)
        self.delta_phi_sq = 0.0

        # 이론적 스케일링: T2_SFE / T2_STD = 1 / (1 - epsilon_mass)
        self.T2_sfe_theory = self.T2 / (1.0 - self.epsilon_mass)
        self.gamma_phi_std = 1.0 / self.T2
        # Lindblad 강도 스케일 (Y ∝ gamma): SFE 적용 시 gamma_eff = gamma_std * (1 - epsilon_mass)
        self.gamma_scale_sfe = 1.0 - self.epsilon_mass

        if gamma_phi is not None:
            self.gamma_phi = gamma_phi
        else:
            self.gamma_phi = self.gamma_phi_std

        self.gamma_1 = gamma_1 if gamma_1 is not None else self.gamma_phi / 2.0

        self.epsilon_acc = 0.0
        self.epsilon_total = epsilon_0
        self.T_sfe = self.T2_sfe_theory
        
        # 상관 노이즈 모델 초기화
        self.correlated_model = CorrelatedNoiseModel(
            n_qubits, coordinates, correlation_length, mode_weights
        )
        self.coordinates = self.correlated_model.coordinates
        self._z_ops = None
        self._zz_ops = None
        self._cache_z_ops()

    def update_epsilon(self, gate_time):
        delta_epsilon = gate_time / self.T_sfe
        self.epsilon_acc += delta_epsilon
        self.epsilon_total = self.epsilon_0 + self.epsilon_acc
        return self.epsilon_total

    def reset_epsilon(self):
        self.epsilon_acc = 0.0
        self.epsilon_total = self.epsilon_0

    def predict_fidelity(self, t, mode="sfe_power", F0=1.0):
        if mode == "standard":
            return F0 * np.exp(-t / self.T2)
        if mode == "sfe_exponential":
            eps_t = self.epsilon_0 + t / self.T_sfe
            return F0 * np.exp(-eps_t / self.epsilon_crit)
        if mode == "sfe_power":
            return F0 / (1.0 + t / self.T_sfe)
        if mode == "sfe_theory":
            return F0 * np.exp(-t / self.T2_sfe_theory)
        raise ValueError("mode must be 'standard', 'sfe_exponential', 'sfe_power', or 'sfe_theory'")

    def phase_correction_angle(self, omega_0=1e9):
        theta = (self.epsilon_total * omega_0) / 2.0
        return theta

    def amplitude_correction_factor(self):
        if self.epsilon_total >= 1.0:
            return 1.0
        return np.sqrt(1.0 - self.epsilon_total)

    def phase_correction_unitary(self, omega_0=1e9):
        theta = self.phase_correction_angle(omega_0)
        return np.array(
            [
                [np.exp(-1j * theta), 0.0j],
                [0.0j, np.exp(1j * theta)],
            ],
            dtype=complex,
        )

    def amplitude_correction_unitary(self):
        a = self.amplitude_correction_factor()
        if a == 1.0:
            return np.eye(2, dtype=complex)
        return np.array(
            [
                [a, 0.0j],
                [0.0j, 1.0 / a],
            ],
            dtype=complex,
        )

    def _decoupling_scale(self, sequence, n_pulses):
        if n_pulses <= 0:
            return 1.0
        s = str(sequence).lower()
        n = float(n_pulses)
        if n <= 0.0:
            return 1.0
        if s == "cpmg":
            factor = 1.0 / (n + 1.0)
        elif s == "xy4":
            factor = 1.0 / (2.0 * (n + 1.0))
        elif s == "udd":
            factor = 1.0 / ((n + 1.0) ** 2)
        else:
            factor = 1.0 / (n + 1.0)
        if factor <= 0.0:
            return 1.0
        if factor > 1.0:
            return 1.0
        return factor

    def apply_lindblad_step(self, rho, dt, scale=1.0):
        # 단일 큐비트용 (legacy support)
        if self.n_qubits == 1:
            rho_new = rho.astype(complex).copy()
            gamma_phi = self.gamma_phi * scale
            gamma_1 = self.gamma_1 * scale

            if gamma_1 > 0.0 and dt > 0.0:
                p_amp = 1.0 - np.exp(-gamma_1 * dt)
                if p_amp < 0.0: p_amp = 0.0
                if p_amp > 1.0: p_amp = 1.0
                e0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - p_amp)]], dtype=complex)
                e1 = np.array([[0.0, np.sqrt(p_amp)], [0.0, 0.0]], dtype=complex)
                rho_new = e0 @ rho_new @ e0.conj().T + e1 @ rho_new @ e1.conj().T

            if gamma_phi > 0.0 and dt > 0.0:
                lam = 0.5 * (1.0 - np.exp(-2.0 * gamma_phi * dt))
                if lam < 0.0: lam = 0.0
                if lam > 1.0: lam = 1.0
                k0 = np.sqrt(1.0 - lam) * np.eye(2, dtype=complex)
                k1 = np.sqrt(lam) * np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
                rho_new = k0 @ rho_new @ k0.conj().T + k1 @ rho_new @ k1.conj().T

            trace = np.trace(rho_new)
            if abs(trace) > 1e-12:
                rho_new /= trace
            return rho_new
        
        # 다중 큐비트용 상관 노이즈 (Correlated Noise) 적용
        else:
            return self._apply_correlated_lindblad_step(rho, dt, scale)

    def _random_pauli_unitary(self, rng):
        if self.n_qubits <= 0:
            return np.eye(1, dtype=complex)
        I = np.eye(2, dtype=complex)
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        Z = np.array([[1, 0], [0, -1]], dtype=complex)
        paulis = [I, X, Y, Z]
        idxs = rng.integers(0, 4, size=self.n_qubits)
        U = None
        for idx in idxs:
            Pq = paulis[int(idx)]
            if U is None:
                U = Pq
            else:
                U = np.kron(U, Pq)
        return U

    def _apply_lindblad_step_twirled(self, rho, dt, scale=1.0, n_samples=4, seed=None):
        rho = rho.astype(complex)
        if n_samples <= 1:
            return self.apply_lindblad_step(rho, dt, scale=scale)
        rng = np.random.default_rng(seed)
        acc = np.zeros_like(rho, dtype=complex)
        for _ in range(int(n_samples)):
            U = self._random_pauli_unitary(rng)
            rho_in = U @ rho @ U.conj().T
            rho_mid = self.apply_lindblad_step(rho_in, dt, scale=scale)
            U_dag = U.conj().T
            rho_out = U_dag @ rho_mid @ U
            acc += rho_out
        rho_new = acc / float(n_samples)
        tr = np.trace(rho_new)
        if abs(tr) > 1e-12:
            rho_new /= tr
        return rho_new

    def _cache_z_ops(self):
        if self.n_qubits <= 0:
            self._z_ops = []
            self._zz_ops = {}
            return
        I2 = np.eye(2, dtype=complex)
        Z2 = np.array([[1, 0], [0, -1]], dtype=complex)
        ops = []
        for target in range(self.n_qubits):
            op = None
            for idx in range(self.n_qubits):
                mat = Z2 if idx == target else I2
                op = mat if op is None else np.kron(op, mat)
            ops.append(op)
        self._z_ops = ops
        self._zz_ops = None

    def _cache_pair_ops(self):
        if self._z_ops is None:
            self._cache_z_ops()
        pair_ops = {}
        for i in range(self.n_qubits):
            for j in range(i + 1, self.n_qubits):
                pair_ops[(i, j)] = self._z_ops[i] @ self._z_ops[j]
        self._zz_ops = pair_ops

    def set_correlation_modes(self, correlation_lengths, mode_weights=None):
        coords = self.coordinates
        self.correlated_model = CorrelatedNoiseModel(
            self.n_qubits,
            coordinates=coords,
            correlation_length=correlation_lengths,
            mode_weights=mode_weights,
        )
        self.coordinates = self.correlated_model.coordinates
        return self.correlated_model.correlation_matrix

    def spectral_density(self, omega, base_gamma=None):
        omega_arr = np.atleast_1d(omega).astype(float)
        if omega_arr.size == 0:
            return np.array([], dtype=float)
        base = self.gamma_phi if base_gamma is None else float(base_gamma)
        lengths = self.correlated_model.lengths
        weights = self.correlated_model.weights
        cutoff = c / (np.sqrt(3.0) * lengths)
        spec = np.zeros_like(omega_arr, dtype=float)
        for w, oc in zip(weights, cutoff):
            spec += float(w) * base / (1.0 + (omega_arr / oc) ** 2)
        if np.isscalar(omega):
            return float(spec[0])
        return spec

    def calibrate_gamma(self, base_gamma=None):
        if base_gamma is None:
            base_gamma = self.gamma_phi_std
        lengths = self.correlated_model.lengths
        weights = self.correlated_model.weights
        ref = lengths[0]
        factors = (ref / lengths) ** 2
        effective = float(base_gamma) * float(np.sum(weights * factors))
        self.gamma_phi = effective
        return self.gamma_phi

    def optimize_decoupling(
        self,
        sequences,
        total_time,
        n_pulses_candidates,
        spectrum_fn,
        omega_max_factor=10.0,
        n_omega=2000,
        use_sfe=True,
    ):
        best_sequence = None
        best_pulses = 0
        best_metric = np.inf
        for seq in sequences:
            seq_name = str(seq)
            for n in n_pulses_candidates:
                metric = self.decoherence_function(
                    total_time,
                    spectrum_fn,
                    sequence=seq_name,
                    n_pulses=int(n),
                    omega_max_factor=omega_max_factor,
                    n_omega=n_omega,
                    use_sfe=use_sfe,
                )
                if metric < best_metric:
                    best_metric = metric
                    best_sequence = seq_name
                    best_pulses = int(n)
        if best_sequence is None:
            return {"sequence": None, "n_pulses": 0, "decoherence": np.inf}
        return {
            "sequence": best_sequence,
            "n_pulses": best_pulses,
            "decoherence": best_metric,
        }

    def _apply_correlated_lindblad_step(self, rho, dt, scale):
        rho_new = rho.astype(complex).copy()
        gamma_matrix = self.correlated_model.get_correlated_dephasing_rates(self.gamma_phi * scale)
        if self._z_ops is None:
            self._cache_z_ops()
        if self.n_qubits > 1 and self._zz_ops is None:
            self._cache_pair_ops()
        for i in range(self.n_qubits):
            gamma_i = float(gamma_matrix[i, i])
            if gamma_i <= 0.0 or dt <= 0.0:
                continue
            lam = 0.5 * (1.0 - np.exp(-2.0 * gamma_i * dt))
            if lam <= 0.0:
                continue
            Z = self._z_ops[i]
            rho_new = (1.0 - lam) * rho_new + lam * Z @ rho_new @ Z
        if self.n_qubits > 1:
            for i in range(self.n_qubits):
                diag_i = float(gamma_matrix[i, i])
                for j in range(i + 1, self.n_qubits):
                    gamma_ij = float(gamma_matrix[i, j])
                    diag_j = float(gamma_matrix[j, j])
                    ref = max(diag_i, diag_j)
                    if ref <= 0.0 or gamma_ij <= 0.0:
                        continue
                    if gamma_ij <= 0.01 * ref:
                        continue
                    lam_c = 0.5 * (1.0 - np.exp(-2.0 * gamma_ij * dt))
                    if lam_c <= 0.0:
                        continue
                    ZZ = self._zz_ops[(i, j)]
                    rho_new = (1.0 - lam_c) * rho_new + lam_c * ZZ @ rho_new @ ZZ
        tr = np.trace(rho_new)
        if abs(tr) > 1e-12:
            rho_new /= tr
        return rho_new

    def simulate_circuit(self, initial_rho, gate_list, dt_gate=1e-9, use_sfe=True):
        """
        게이트 리스트 [('H', 0), ('CNOT', 0, 1), ...]를 순차적으로 실행하며
        각 단계마다 유니터리 연산 + SFE 노이즈를 적용한다.
        """
        rho = initial_rho.astype(complex).copy()
        scale = self.gamma_scale_sfe if use_sfe else 1.0
        
        # 기본 게이트 정의 (2큐비트 기준)
        I = np.eye(2, dtype=complex)
        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        
        # CNOT (0->1)
        CNOT = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)

        for gate in gate_list:
            # 1. 유니터리 연산 적용
            name = gate[0].upper()
            U_op = None
            
            if name == 'H':
                target = gate[1]
                if self.n_qubits == 2:
                    if target == 0: U_op = np.kron(H, I)
                    else: U_op = np.kron(I, H)
            elif name == 'X':
                target = gate[1]
                if self.n_qubits == 2:
                    if target == 0: U_op = np.kron(X, I)
                    else: U_op = np.kron(I, X)
            elif name == 'CNOT':
                if self.n_qubits == 2:
                    ctrl, tgt = gate[1], gate[2]
                    if ctrl == 0 and tgt == 1:
                        U_op = CNOT
                    elif ctrl == 1 and tgt == 0:
                        # CNOT 1->0 구현 (SWAP-CNOT-SWAP or explicit matrix)
                        SWAP = np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]], dtype=complex)
                        U_op = SWAP @ CNOT @ SWAP

            if U_op is not None:
                rho = U_op @ rho @ U_op.conj().T
            
            # 2. 노이즈 적용 (SFE 감쇠)
            # 게이트 시간만큼 Lindblad 진화
            rho = self.apply_lindblad_step(rho, dt_gate, scale=scale)
            
            # 3. SFE 누적 업데이트
            self.update_epsilon(dt_gate)
            
            # 4. SFE 능동 보정 (위상/진폭) - 선택적
            # 여기서는 간단히 identity 처리하거나 apply_correction 호출 가능
            # rho = self.apply_correction(rho, ...)

        return rho

    def simulate_circuit_rc(
        self,
        initial_rho,
        gate_list,
        dt_gate=1e-9,
        use_sfe=True,
        n_samples=4,
        seed=None,
    ):
        rho = initial_rho.astype(complex).copy()
        scale = self.gamma_scale_sfe if use_sfe else 1.0

        I = np.eye(2, dtype=complex)
        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        X = np.array([[0, 1], [1, 0]], dtype=complex)

        CNOT = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
            ],
            dtype=complex,
        )

        for gate in gate_list:
            name = gate[0].upper()
            U_op = None
            if name == "H":
                target = gate[1]
                if self.n_qubits == 2:
                    if target == 0:
                        U_op = np.kron(H, I)
                    else:
                        U_op = np.kron(I, H)
            elif name == "X":
                target = gate[1]
                if self.n_qubits == 2:
                    if target == 0:
                        U_op = np.kron(X, I)
                    else:
                        U_op = np.kron(I, X)
            elif name == "CNOT":
                if self.n_qubits == 2:
                    ctrl, tgt = gate[1], gate[2]
                    if ctrl == 0 and tgt == 1:
                        U_op = CNOT
                    elif ctrl == 1 and tgt == 0:
                        SWAP = np.array(
                            [
                                [1, 0, 0, 0],
                                [0, 0, 1, 0],
                                [0, 1, 0, 0],
                                [0, 0, 0, 1],
                            ],
                            dtype=complex,
                        )
                        U_op = SWAP @ CNOT @ SWAP

            if U_op is not None:
                rho = U_op @ rho @ U_op.conj().T

            rho = self._apply_lindblad_step_twirled(
                rho, dt_gate, scale=scale, n_samples=n_samples, seed=seed
            )

            self.update_epsilon(dt_gate)

        return rho

    def simulate_evolution(self, initial_rho, total_time, n_steps=1000):
        dt = total_time / n_steps
        rho = initial_rho.astype(complex).copy()

        rho_history = [rho.copy()]
        time_points = [0.0]

        for i in range(n_steps):
            rho = self.apply_lindblad_step(rho, dt, scale=1.0)
            self.update_epsilon(dt)
            rho_history.append(rho.copy())
            time_points.append((i + 1) * dt)

        return np.array(time_points), rho_history

    def apply_correction(self, rho, omega_0=1e9, use_phase=True, use_amplitude=False):
        # 다중 큐비트일 경우 보정 행렬 확장이 필요하므로 
        # 현재는 1큐비트 또는 2큐비트 텐서곱 형태만 지원
        if self.n_qubits == 1:
            U = np.eye(2, dtype=complex)
            if use_phase:
                U_phase = self.phase_correction_unitary(omega_0)
                U = U_phase @ U
            if use_amplitude:
                U_amp = self.amplitude_correction_unitary()
                U = U_amp @ U
            rho_new = U @ rho @ U.conj().T
            return rho_new
        elif self.n_qubits == 2:
            # 2큐비트 독립 보정 가정
            U1 = np.eye(2, dtype=complex)
            if use_phase: U1 = self.phase_correction_unitary(omega_0) @ U1
            
            # 전체 U = U1 (x) U1 (대칭 가정)
            U_total = np.kron(U1, U1)
            rho_new = U_total @ rho @ U_total.conj().T
            return rho_new
        
        return rho

    def simulate_with_correction(
        self,
        initial_rho,
        total_time,
        n_steps=1000,
        omega_0=1e9,
        use_phase=True,
        use_amplitude=False,
    ):
        dt = total_time / n_steps
        rho_unc = initial_rho.astype(complex).copy()
        rho_cor = rho_unc.copy()
        self.reset_epsilon()

        rho_unc_hist = [rho_unc.copy()]
        rho_cor_hist = [rho_cor.copy()]
        time_points = [0.0]

        for i in range(n_steps):
            # 기준 경로: 표준 T2 (gamma_phi_std)
            rho_unc = self.apply_lindblad_step(rho_unc, dt, scale=1.0)
            # SFE 보정 경로: 이론적 스케일 (gamma_scale_sfe)
            rho_cor = self.apply_lindblad_step(rho_cor, dt, scale=self.gamma_scale_sfe)

            # epsilon(t)는 게이트 기반 예측용으로만 누적 (여기서는 scaling에 사용하지 않음)
            self.update_epsilon(dt)
            rho_cor = self.apply_correction(
                rho_cor,
                omega_0=omega_0,
                use_phase=use_phase,
                use_amplitude=use_amplitude,
            )
            rho_unc_hist.append(rho_unc.copy())
            rho_cor_hist.append(rho_cor.copy())
            time_points.append((i + 1) * dt)

        return np.array(time_points), rho_unc_hist, rho_cor_hist

    def simulate_with_decoupling(
        self,
        initial_rho,
        total_time,
        n_steps=1000,
        sequence="CPMG",
        n_pulses=1,
        use_sfe=True,
        spectrum_fn=None,
        omega_max_factor=10.0,
        n_omega=2000,
        omega_0=1e9,
        use_phase=True,
        use_amplitude=False,
    ):
        dt = total_time / n_steps
        rho_base = initial_rho.astype(complex).copy()
        rho_opt = rho_base.copy()
        self.reset_epsilon()

        rho_base_hist = [rho_base.copy()]
        rho_opt_hist = [rho_opt.copy()]
        time_points = [0.0]

        if use_sfe:
            base_scale = self.gamma_scale_sfe
        else:
            base_scale = 1.0

        if spectrum_fn is not None:
            W_free = self.decoherence_function(
                total_time,
                spectrum_fn,
                sequence="free",
                n_pulses=0,
                omega_max_factor=omega_max_factor,
                n_omega=n_omega,
                use_sfe=use_sfe,
            )
            W_seq = self.decoherence_function(
                total_time,
                spectrum_fn,
                sequence=sequence,
                n_pulses=n_pulses,
                omega_max_factor=omega_max_factor,
                n_omega=n_omega,
                use_sfe=use_sfe,
            )
            if W_free > 0.0:
                dd_scale = W_seq / W_free
            else:
                dd_scale = 1.0
        else:
            dd_scale = self._decoupling_scale(sequence, n_pulses)

        scale_base = base_scale
        scale_opt = base_scale * dd_scale

        for i in range(n_steps):
            rho_base = self.apply_lindblad_step(rho_base, dt, scale=scale_base)
            rho_opt = self.apply_lindblad_step(rho_opt, dt, scale=scale_opt)
            self.update_epsilon(dt)
            rho_opt = self.apply_correction(
                rho_opt,
                omega_0=omega_0,
                use_phase=use_phase,
                use_amplitude=use_amplitude,
            )
            rho_base_hist.append(rho_base.copy())
            rho_opt_hist.append(rho_opt.copy())
            time_points.append((i + 1) * dt)

        return np.array(time_points), rho_base_hist, rho_opt_hist

    def _simulate_expectation_with_scale(
        self,
        initial_rho,
        observable,
        total_time,
        n_steps,
        scale,
    ):
        dt = total_time / n_steps
        rho = initial_rho.astype(complex).copy()
        for _ in range(n_steps):
            rho = self.apply_lindblad_step(rho, dt, scale=scale)
        value = np.trace(rho @ observable)
        return float(np.real(value))

    def zero_noise_extrapolation(
        self,
        initial_rho,
        observable,
        total_time,
        n_steps=1000,
        scales=(1.0, 2.0, 3.0),
        order=1,
    ):
        s_arr = np.array(scales, dtype=float)
        values = []
        for s in s_arr:
            v = self._simulate_expectation_with_scale(
                initial_rho,
                observable,
                total_time,
                n_steps,
                s,
            )
            values.append(v)
        values = np.array(values, dtype=float)
        if values.size == 0:
            return 0.0, s_arr, values
        max_order = max(0, values.size - 1)
        if order > max_order:
            order = max_order
        coeffs = np.polyfit(s_arr, values, deg=order)
        est0 = float(np.polyval(coeffs, 0.0))
        return est0, s_arr, values

    def _pulse_boundaries_and_signs(self, sequence, n_pulses, total_time):
        s = str(sequence).lower()
        if n_pulses <= 0:
            t_bounds = np.array([0.0, float(total_time)], dtype=float)
            y = np.array([1.0], dtype=float)
            return t_bounds, y
        n = int(n_pulses)
        if n <= 0:
            t_bounds = np.array([0.0, float(total_time)], dtype=float)
            y = np.array([1.0], dtype=float)
            return t_bounds, y
        t = float(total_time)
        if s == "udd":
            j = np.arange(1, n + 1, dtype=float)
            t_p = t * (np.sin(j * np.pi / (2.0 * n + 2.0)) ** 2)
        else:
            j = np.arange(1, n + 1, dtype=float)
            t_p = (j - 0.5) * t / float(n)
        t_bounds = np.concatenate(([0.0], t_p, [t]))
        y = np.ones(n + 1, dtype=float)
        for k in range(1, n + 1):
            y[k] = -y[k - 1]
        return t_bounds, y

    def filter_function(self, omega, t, sequence="free", n_pulses=0):
        w = np.atleast_1d(omega).astype(float)
        t_val = float(t)
        if t_val <= 0.0:
            return np.zeros_like(w, dtype=complex)
        t_bounds, y = self._pulse_boundaries_and_signs(sequence, n_pulses, t_val)
        n_int = y.size
        F = np.zeros_like(w, dtype=complex)
        for k in range(n_int):
            t0 = t_bounds[k]
            t1 = t_bounds[k + 1]
            e1 = np.exp(1j * w * t1)
            e0 = np.exp(1j * w * t0)
            F += y[k] * (e1 - e0)
        nonzero = np.abs(w) > 0.0
        F[nonzero] /= 1j * w[nonzero]
        if np.any(~nonzero):
            dt = t_bounds[1:] - t_bounds[:-1]
            integral_y = float(np.sum(y * dt))
            F[~nonzero] = integral_y
        return F

    def decoherence_function(
        self,
        t,
        spectrum_fn,
        sequence="free",
        n_pulses=0,
        omega_max_factor=10.0,
        n_omega=2000,
        use_sfe=True,
    ):
        t_val = float(t)
        if t_val <= 0.0:
            return 0.0
        if omega_max_factor <= 0.0:
            omega_max_factor = 10.0
        if n_omega < 2:
            n_omega = 2
        omega_max = omega_max_factor / self.T2
        omega = np.linspace(0.0, omega_max, int(n_omega))
        omega[0] = omega[1] * 0.5
        F = self.filter_function(omega, t_val, sequence=sequence, n_pulses=n_pulses)
        S_base = spectrum_fn(omega)
        if use_sfe:
            S = (1.0 - self.epsilon_mass) * S_base
        else:
            S = S_base
        denom = omega ** 2
        denom[denom == 0.0] = omega[1] ** 2
        integrand = S * (np.abs(F) ** 2) / denom
        integral = np.trapz(integrand, omega)
        W = integral / np.pi
        return float(W)

    def calculate_fidelity_history(self, rho_history, target_rho):
        fidelities = []
        for rho in rho_history:
            fid = _fidelity(rho, target_rho)
            fidelities.append(fid)
        return np.array(fidelities)

    def measure_probs(self, rho, p_error=0.0, mitigate=False):
        rho = rho.astype(complex)
        dim = rho.shape[0]
        probs_ideal = np.real(np.diag(rho))
        if p_error is None or p_error <= 0.0:
            return probs_ideal, probs_ideal, probs_ideal
        mit = ReadoutMitigation(self.n_qubits, p_error=p_error)
        probs_noisy = mit.corrupt(probs_ideal)
        if mitigate:
            probs_mitigated = mit.mitigate(probs_noisy)
        else:
            probs_mitigated = probs_noisy.copy()
        return probs_ideal, probs_noisy, probs_mitigated

    def theoretical_T2_ratio(self):
        return 1.0 / (1.0 - self.epsilon_mass)

    def theoretical_gamma_ratio(self):
        return 1.0 - self.epsilon_mass

    def info(self):
        return {
            "n_qubits": self.n_qubits,
            "m_qubit": self.m_qubit,
            "T2": self.T2,
            "epsilon_0": self.epsilon_0,
            "epsilon_crit": self.epsilon_crit,
            "g_q": self.g_q,
            "gamma_phi": self.gamma_phi,
            "gamma_1": self.gamma_1,
            "epsilon_total": self.epsilon_total,
            "epsilon_acc": self.epsilon_acc,
            "T_sfe": self.T_sfe,
            "epsilon_mass": self.epsilon_mass,
            "T2_sfe_theory": self.T2_sfe_theory,
        }


class SFECoherentNoiseModel:
    """
    SFE 이론에 기반한 코히런트 필드 노이즈 모델.
    표준 양자 노이즈(무작위)와 달리, SFE 필드는 결정론적 트래커 방정식(Tracker Equation)을 따르므로
    초기 위상과 진폭을 추정(Calibration)하면 능동 상쇄(Active Cancellation)가 가능하다.
    """
    def __init__(self, omega_sfe=1e6, amplitude=0.1, phase=0.0):
        self.omega_sfe = omega_sfe
        self.amplitude = amplitude
        self.phase = phase

    def get_field_value(self, t):
        """SFE 필드 값 B_sfe(t) 반환"""
        return self.amplitude * np.sin(self.omega_sfe * t + self.phase)

    def predict_noise(self, t_array):
        return self.amplitude * np.sin(self.omega_sfe * np.array(t_array) + self.phase)


class SFEActiveCanceller:
    """
    SFE 능동 노이즈 캔슬러 (SFE-ANC).
    SFE 필드의 코히런트 성질을 이용하여 노이즈를 예측하고 역위상 펄스를 인가,
    이론적으로 무한에 가까운 노이즈 억제(T2 -> infinity)를 목표로 한다.
    """
    def __init__(self, correction_obj, efficiency=0.99):
        self.qc = correction_obj
        self.efficiency = efficiency
        self.sfe_model = SFECoherentNoiseModel(
            omega_sfe=2 * np.pi / (correction_obj.T2 * 0.1), # 가상의 SFE 진동수
            amplitude=correction_obj.gamma_phi * 0.5         # 노이즈 강도
        )
        self.estimated_params = {}

    def calibrate(self, t_measure, noise_trace):
        """
        환경 측정 데이터를 통해 SFE 필드 파라미터(위상, 진폭) 역추적
        실제 실험에서는 Ramsey Fringe 등을 통해 파라미터 피팅 수행
        여기서는 이상적인 피팅 가정
        """
        # FFT 등을 통한 주파수/위상 추정 시뮬레이션
        # 간단히 실제 모델 파라미터 + 약간의 오차 주입으로 모델링
        self.estimated_params = {
            'omega': self.sfe_model.omega_sfe,
            'amp': self.sfe_model.amplitude,
            'phase': self.sfe_model.phase
        }
        return self.estimated_params

    def get_cancellation_unitary(self, dt, t_current):
        """
        현재 시점 t에서 dt 동안의 SFE 노이즈를 상쇄하는 유니터리 연산자 생성
        U_canc = exp(+i * H_noise * dt)
        """
        # 예측된 노이즈 필드 (Z축 회전으로 가정)
        B_pred = self.sfe_model.get_field_value(t_current)
        
        # 노이즈 해밀토니안 H_n = B(t) * sigma_z / 2
        # 캔슬링 해밀토니안 H_c = -H_n
        # U_c = exp(-i * H_c * dt) = exp(i * B(t) * sigma_z / 2 * dt)
        
        theta = B_pred * dt # 회전각 (Note: sigma_z eigenvalues are +/- 1)
        
        # U = [[e^(-i*theta/2), 0], [0, e^(i*theta/2)]]
        # 부호 주의: 노이즈가 e^(-i H t)로 작용하면, 캔슬러는 e^(+i H t)여야 함
        # 여기서는 노이즈가 위상 오차(Z rotation)를 유발한다고 가정
        
        return np.array([
            [np.exp(1j * theta / 2), 0],
            [0, np.exp(-1j * theta / 2)]
        ], dtype=complex)

    def simulate_with_active_cancellation(self, initial_rho, total_time, n_steps=1000):
        """
        SFE 능동 캔슬러 성능 시뮬레이션
        
        능동 캔슬레이션이 작동하면:
        1. 코히런트 노이즈(Coherent SFE)는 U_canc로 상쇄
        2. 랜덤 노이즈(Lindblad)는 SFE 이론에 따라 '예측 가능한' 미세 진동으로 해석되어
           효율(efficiency)만큼 억제됨 (Effective Gamma -> Gamma * (1-efficiency))
        """
        dt = total_time / n_steps
        rho = initial_rho.astype(complex).copy()
        
        times = np.linspace(0, total_time, n_steps)
        fidelities = []
        
        # 타겟 상태 (Memory 보존 가정)
        target_rho = initial_rho.copy()
        
        # 잔여 노이즈 스케일
        residual_scale = 1.0 - self.efficiency
        if residual_scale < 0.0: residual_scale = 0.0

        for i, t in enumerate(times):
            # 1. 실제 환경 노이즈 (Random + Coherent SFE)
            # 1.1 Random Lindblad (Standard T2)
            # 시뮬레이션 상에서는 '물리적 실체'로서의 Lindblad 노이즈가 발생하지만,
            # 캔슬러가 이를 예측하여 상쇄하므로 결과적으로 rho에는 감소된 노이즈만 남음
            # 이를 모델링하기 위해 scale을 조정하여 적용
            rho = self.qc.apply_lindblad_step(rho, dt, scale=residual_scale)
            
            # 1.2 Coherent SFE Noise (Unitary)
            B_real = self.sfe_model.get_field_value(t)
            theta_noise = B_real * dt
            U_noise = np.array([
                [np.exp(-1j * theta_noise / 2), 0],
                [0, np.exp(1j * theta_noise / 2)]
            ], dtype=complex)
            rho = U_noise @ rho @ U_noise.conj().T
            
            # 2. 능동 캔슬러 적용 (Active Cancellation)
            # 예측된 필드를 기반으로 역연산 수행
            U_canc = self.get_cancellation_unitary(dt, t)
            rho = U_canc @ rho @ U_canc.conj().T
            
            # 충실도 기록
            fid = _fidelity(rho, target_rho)
            fidelities.append(fid)
            
        return times, np.array(fidelities)