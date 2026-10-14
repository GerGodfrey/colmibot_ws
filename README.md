# Proyecto final
**Autores:** 
+ Elena Sofia Luna Palacio
- Luis Gerardo Godfrey Castañeda
- Tania Ariadna Dominguez Palma

## Teleoperación con joystick comercial Turtlesim 
### Descripción breve
En esta actividad se implementó la comunicación entre un control de videojuego y ROS 2 mediante el paquete `joy`. Se desarrolló un nodo controlador que procesa las lecturas analógicas del joystick para convertirlas en comandos de velocidad (`geometry_msgs/msg/Twist`) y operar el simulador **Turtlesim**. Finalmente, se creó un archivo *launch* para automatizar el inicio de todos los nodos del sistema.

### Funcionamiento
- **Tópicos utilizados:** 
  - `/joy`: Recibe el estado del control mediante el mensaje `sensor_msgs/msg/Joy`.
  - `/turtle1/cmd_vel`: Publica comandos de movimiento a la tortuga mediante el mensaje `geometry_msgs/msg/Twist`.

- **Nodos involucrados:**
  - `joy_node`: Captura los eventos del joystick comercial y los publica en `/joy`.
  - `play_station_turtle_controller`: Escucha el tópico `/joy`, extrae los valores de los ejes analógicos (`axes[3]` y `axes[4]`), los escala e interpreta para generar velocidades lineales y angulares, y los publica en `/turtle1/cmd_vel`.
  - `turtlesim_node`: Nodo de simulación gráfica que recibe las velocidades y mueve la tortuga.

### Comandos utilizados
Para ejecutar el proyecto desde una terminal
```bash
ros2 launch colmibotbasics play_station_turtle_controller.launch.py
```

### Problemas encontrados
**Problema**: 

**Solucion**: 

### Video de funcionamiento
