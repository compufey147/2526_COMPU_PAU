# ================================================================================
# ANIMACION SISTEMA SOLAR (VERSIÓN CON COLORES REALISTAS)
# ================================================================================

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import numpy as np

# Parámetros
# ========================================
file_in = "planets_data.dat" # Nombre del fichero de datos
file_out = "planetas" # Nombre del fichero de salida (sin extensión)

# Límites de los ejes X e Y (Ajustados para no verse aplastado)
# Límites de los ejes X e Y (Ajustados para ver hasta Neptuno)
x_min = -35
x_max = 35
y_min = -35 
y_max = 35

interval = 20 # Tiempo entre fotogramas (bajado un poco para que vaya más fluido)
show_trail = True # Muestra la "estela" del planeta
trail_width = 1 # Ancho de la estela
save_to_file = False # Puesto a False para que salte la ventana en tu pantalla
dpi = 150 # Calidad del vídeo de salida

# -------------------------------------------------------------------
# ¡NUEVO! COLORES Y TAMAÑOS REALISTAS
# El orden asume: Sol, Mercurio, Venus, Tierra, Marte, Júpiter, Saturno, Urano, Neptuno
# -------------------------------------------------------------------
planet_colors = [
    '#FFCC00', # Sol: Amarillo brillante
    '#9E9E9E', # Mercurio: Gris roca
    '#E3BB76', # Venus: Ocre / Amarillo pálido
    '#2A82D7', # Tierra: Azul océano
    '#C1440E', # Marte: Rojo óxido
    '#D39C7E', # Júpiter: Marrón/Naranja claro
    '#E2BF7D', # Saturno: Dorado pálido
    '#4B70DD', # Urano: Azul claro verdoso
    '#274687'  # Neptuno: Azul oscuro
]

# Radios visuales (proporcionales para que se vea bien en pantalla, no a escala estricta)
planet_radius = [0.4, 0.05, 0.1, 0.1, 0.08, 0.25, 0.2, 0.15, 0.15]


# Lectura del fichero de datos
# ========================================
with open(file_in, "r") as f:
    data_str = f.read()

frames_data = list()

for frame_data_str in data_str.split("\n\n"):
    frame_data = list()
    for planet_pos_str in frame_data_str.split("\n"):
        planet_pos = np.fromstring(planet_pos_str, sep=",")
        if planet_pos.size > 0:
            frame_data.append(np.fromstring(planet_pos_str, sep=","))
    if len(frame_data) > 0: # Evitar añadir bloques vacíos al final del archivo
        frames_data.append(frame_data)

nplanets = len(frames_data[0])


# Creación de la animación/gráfico
# ========================================
# Crea los objetos figure y axis con fondo oscuro para simular el espacio
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_facecolor('#050510') # Fondo negro espacial
fig.patch.set_facecolor('#050510')

ax.axis("equal")
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.tick_params(colors='white') # Números de los ejes en blanco

# Asegurarse de que tenemos suficientes colores/radios si hay menos/más planetas en el .dat
if nplanets > len(planet_colors):
    # Si hay más cuerpos por algún motivo, rellenar con blanco
    planet_colors += ['white'] * (nplanets - len(planet_colors))
    planet_radius += [0.1] * (nplanets - len(planet_radius))

planet_points = list()
planet_trails = list()

# Pintar el primer fotograma
for i, planet_pos in enumerate(frames_data[0]):
    x, y = planet_pos
    
    # Creamos el círculo pasándole el color de nuestra lista
    planet_point = Circle((x, y), planet_radius[i], color=planet_colors[i], zorder=4)
    ax.add_artist(planet_point)
    planet_points.append(planet_point)

    if show_trail:
        # La estela coge el mismo color, le bajamos la opacidad (alpha) para que quede más elegante
        planet_trail, = ax.plot(
                x, y, "-", linewidth=trail_width,
                color=planet_colors[i], alpha=0.6, zorder=3)
        planet_trails.append(planet_trail)
 
def update(j_frame, frames_data, planet_points, planet_trails, show_trail):
    for j_planet, planet_pos in enumerate(frames_data[j_frame]):
        x, y = planet_pos
        planet_points[j_planet].center = (x, y)

        if show_trail:
            xs_old, ys_old = planet_trails[j_planet].get_data()
            xs_new = np.append(xs_old, x)
            ys_new = np.append(ys_old, y)
            planet_trails[j_planet].set_data(xs_new, ys_new)

    return planet_points + planet_trails

def init_anim():
    if show_trail:
        for j_planet in range(nplanets):
            planet_trails[j_planet].set_data(list(), list())
    return planet_points + planet_trails

nframes = len(frames_data)

if nframes > 1:
    animation = FuncAnimation(
            fig, update, init_func=init_anim,
            fargs=(frames_data, planet_points, planet_trails, show_trail),
            frames=len(frames_data), blit=True, interval=interval)

    if save_to_file:
        animation.save("{}.mp4".format(file_out), dpi=dpi)
    else:
        plt.show()
else:
    if save_to_file:
        fig.savefig("{}.pdf".format(file_out))
    else:
        plt.show()

#prueba de git forzando cambio
