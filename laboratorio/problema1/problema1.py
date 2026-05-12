import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle

# =============================================================================
# 1. PARÁMETROS Y ESCALAS DE LA SIMULACIÓN
# =============================================================================
C_DIST = 149.59787e9  # 1 AU en metros
M_SUN = 1988500e24    # Masa solar en kg
V_UNIT = 29.78469e3   # Unidad de velocidad en m/s 
T_UNIT_DAYS = 58.13   # Unidad temporal en días

# [Masa (10^24 kg), Distancia Perihelio (10^9 m), Velocidad Perihelio (10^3 m/s)]
datos_reales = {
    "Sol":     [M_SUN, 0.0, 0.0],
    "Mercurio":[0.3301, 46.00, 58.98],
    "Venus":   [4.8676, 107.48, 35.26],
    "Tierra":  [5.9726, 147.09, 30.29],
    "Marte":   [0.64174, 206.62, 26.50],
    "Jupiter": [1898.3, 740.52, 13.72],
    "Saturno": [568.36, 1352.55, 10.18],
    "Urano":   [86.816, 2741.30, 7.11],
    "Neptuno": [102.42, 4444.45, 5.50]
}

periodos_reales = {
    "Mercurio": 88.0, "Venus": 224.7, "Tierra": 365.2, "Marte": 687.0,
    "Jupiter": 4331.0, "Saturno": 10747.0, "Urano": 30589.0, "Neptuno": 59800.0
}

planetas = {}
for nombre, datos in datos_reales.items():
    planetas[nombre] = {
        "m": datos[0] / M_SUN,
        "r": np.array([(datos[1] * 1e9) / C_DIST, 0.0]),
        "v": np.array([0.0, (datos[2] * 1e3) / V_UNIT]),
        "y_prev": 0.0,
        "periodo_medido": None
    }

nombres = list(planetas.keys())
n_planetas = len(nombres)
masas = np.array([planetas[n]["m"] for n in nombres])
posiciones = np.array([planetas[n]["r"] for n in nombres])
velocidades = np.array([planetas[n]["v"] for n in nombres])

# =============================================================================
# FUNCIONES FÍSICAS
# =============================================================================

def calcular_aceleraciones(pos, m):
    n = len(m)
    acc = np.zeros((n, 2))
    for i in range(n):
        for j in range(n):
            if i != j:
                r_ij = pos[i] - pos[j]
                dist2 = np.dot(r_ij, r_ij)
                acc[i] -= m[j] * r_ij / (dist2 * np.sqrt(dist2))
    return acc


def calcular_energia_mecanica(pos, vel, m):
    t_kin = 0.5 * np.sum(m * np.linalg.norm(vel, axis=1)**2)
    u_pot = 0.0
    for i in range(n_planetas):
        for j in range(i + 1, n_planetas):
            dist = np.linalg.norm(pos[i] - pos[j])
            u_pot -= (m[i] * m[j]) / dist
    return t_kin + u_pot


def calcular_momento_angular(pos, vel, m):
    L_total = 0.0
    for i in range(len(m)):
        L_total += m[i] * (pos[i,0]*vel[i,1] - pos[i,1]*vel[i,0])
    return L_total

# =============================================================================
# CONFIGURACIÓN Y BUCLE DE SIMULACIÓN
# =============================================================================

h = 0.005       
t_final = 1400.0   # aumentado para Neptuno
n_pasos = int(t_final / h)

t_array = np.zeros(n_pasos)
energias = np.zeros(n_pasos)
momentos_angulares = np.zeros(n_pasos)
historial_pos = np.zeros((n_pasos, n_planetas, 2))

aceleraciones = calcular_aceleraciones(posiciones, masas)

print("Iniciando simulación numérica..")

for paso in range(n_pasos):
    t = paso * h
    t_array[paso] = t
    historial_pos[paso] = posiciones
    
    energias[paso] = calcular_energia_mecanica(posiciones, velocidades, masas)
    momentos_angulares[paso] = calcular_momento_angular(posiciones, velocidades, masas)
    
    # Detectar periodos
    for i, nombre in enumerate(nombres):
        if nombre != "Sol" and planetas[nombre]["periodo_medido"] is None:
            y_actual = posiciones[i, 1]
            y_prev = planetas[nombre]["y_prev"]
            if y_prev < 0 and y_actual >= 0:
                t_cruce = t - y_actual * h / (y_actual - y_prev)
                planetas[nombre]["periodo_medido"] = t_cruce * T_UNIT_DAYS
            planetas[nombre]["y_prev"] = y_actual

    # Integrador de Verlet
    w = velocidades + 0.5 * h * aceleraciones
    posiciones = posiciones + h * w
    nuevas_aceleraciones = calcular_aceleraciones(posiciones, masas)
    velocidades = w + 0.5 * h * nuevas_aceleraciones
    aceleraciones = nuevas_aceleraciones

# =============================================================================
# RESULTADOS POR CONSOLA
# =============================================================================

print("\n--- ANÁLISIS DE PERIODOS ORBITALES ---")
print(f"{'Planeta':<10} | {'T Real (dias)':<15} | {'T Sim (dias)':<15} | {'Error Relativo'}")
print("-" * 60)

for nombre in nombres:
    if nombre == "Sol": continue
    t_sim = planetas[nombre]["periodo_medido"]
    t_real = periodos_reales[nombre]
    if t_sim:
        error = abs(t_sim - t_real) / t_real
        print(f"{nombre:<10} | {t_real:<15.1f} | {t_sim:<15.1f} | {error:.2e}")
    else:
        print(f"{nombre:<10} | {t_real:<15.1f} | Órbita incompleta   | N/A")

# =============================================================================
# CONSERVACIÓN ENERGÍA Y MOMENTO ANGULAR
# =============================================================================

fig2, (ax1, ax2) = plt.subplots(2,1, figsize=(8,8))

energia_rel = (energias - energias[0]) / abs(energias[0])
ax1.plot(t_array, energia_rel)
ax1.set_title("Conservación Energía Mecánica")
ax1.set_ylabel("Error relativo")
ax1.grid()

mom_rel = (momentos_angulares - momentos_angulares[0]) / abs(momentos_angulares[0])
ax2.plot(t_array, mom_rel)
ax2.set_title("Conservación Momento Angular")
ax2.set_xlabel("Tiempo")
ax2.set_ylabel("Error relativo")
ax2.grid()

plt.tight_layout()
plt.show()

# =============================================================================
# ANIMACIÓN
# =============================================================================

fig, ax = plt.subplots(figsize=(10, 10))
ax.set_facecolor('#050510')
fig.patch.set_facecolor('#050510')

ax.set_xlim(-35, 35)
ax.set_ylim(-35, 35)
ax.set_aspect('equal')
ax.set_title("Sistema Solar Completo", color='white')
ax.tick_params(colors='white')

planet_colors = ['#FFCC00', '#9E9E9E', '#E3BB76', '#2A82D7', '#C1440E', '#D39C7E', '#E2BF7D', '#4B70DD', '#274687']
planet_sizes = [12, 3, 4, 4, 3, 9, 8, 6, 6]

planet_points = []

for i in range(n_planetas):
    ax.plot(historial_pos[:, i, 0], historial_pos[:, i, 1], "-",
            color=planet_colors[i], alpha=0.3, linewidth=1, zorder=2)
    
    orden_z = 3 if i == 0 else 4
    punto, = ax.plot([], [], 'o', color=planet_colors[i],
                     markersize=planet_sizes[i],
                     zorder=orden_z,
                     label=nombres[i])
    planet_points.append(punto)

ax.legend(loc='upper right', fontsize=8,
          labelcolor='white',
          facecolor='black',
          edgecolor='white')


def actualizar(frame):
    paso_anim = frame * 10
    
    if paso_anim >= n_pasos:
        return planet_points
    
    for i in range(n_planetas):
        x = historial_pos[paso_anim, i, 0]
        y = historial_pos[paso_anim, i, 1]
        planet_points[i].set_data([x], [y])
        
    return planet_points

ani = animation.FuncAnimation(fig, actualizar,
                              frames=n_pasos//10,
                              interval=30,
                              blit=True)

plt.show()