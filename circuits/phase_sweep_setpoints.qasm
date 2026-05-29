// Phase setpoint family.
// Generate one circuit per theta in: 0, pi/4, pi/2, 3pi/4, pi.
// Expected single-qubit model: P(1) = sin(theta / 2)^2.
OPENQASM 2.0;
include "qelib1.inc";

qreg q[1];
creg meas[1];

h q[0];
rz(pi/2) q[0];
h q[0];
measure q[0] -> meas[0];
