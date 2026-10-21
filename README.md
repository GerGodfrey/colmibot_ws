# Proyecto final
**Autores:** 
- Elena Sofía Luna Palacio
- Luis Gerardo Godfrey Castañeda
- Tania Ariadna Dominguez Palma

## Teleoperación con joystick comercial Turtlesim 
### Descripción breve
En esta actividad se implementó la comunicación entre un control de videojuego y ROS 2 mediante el paquete `joy`. Se desarrolló un nodo controlador que procesa las lecturas analógicas del joystick para convertirlas en comandos de velocidad (`geometry_msgs/msg/Twist`) y operar el simulador **Turtlesim**. Finalmente, se creó un archivo *launch* para automatizar el inicio de todos los nodos del sistema.

### Funcionamiento
- **Tópicos utilizados:** 
  - `/joy`: Recibe el estado del control mediante el mensaje `sensor_msgs/msg/Joy`. Utilizamos el arreglo de AXES, específicamente los índices 3 y 4 para los ejes X y Y del joystick elegido.
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
**Problema**: La computadora no reconocía el control de Play Station.

**Solucion**: Cambiar de cable mini usb. Identificar uno que fuera de datos, no solo de carga.

### Video de funcionamiento
https://drive.google.com/file/d/1xeWZEY9VAiEY9kjB-hVeuJiEwnarTBqq/view?usp=sharing

## Gemelo Digital Colmibot
### Descripción breve
En esta actividad se creó un gemelo digital del colmibot basado en el diseño de CAD y se integró con ROS2 para poder visualizarlo con Rviz (una herramienta de visualización 3D). Para ello se convirtieron las piezas y sus "mates" en 15 links y 12 joints de URDF (código XML que define al robot).

### Herramientas
- SolidWorks: para procesar el diseño de CAD original
- STL y DAE: la geometría de las piezas
- sw2robot: exportador de SolidWorks para la creación de las mallas
- URDF: los componentes del robot y las relaciones entre estos
- ROS2 Jazzy: creación del modelo del robot
  + `joint_state_publisher`: nodo que permite modificar manualmente el valor de los *joints* (específicamente las de las ruedas) a través de una GUI u luego las publica en el tópico `/joint_states`.
  + `robot_state_publisher`: nodo encargado de calcular y publicar la posición de los componentes del robot a través del tópico `/tf_static`. Utiliza la información recibida en el tópico `/joint_states` para calcular transformaciones de los componentes y las publica en el tópico `/tf`. Además, este nodo publica la descripción del robot (URDF) a través del tópico `/robot_description`.
  + `rviz2`: permite mostrar el robot de forma gráfica.
    
### Implementación
Con base en los diseños de CAD se utilizó sw2robot para exportar los componentes al formato URDf. Así, se generaron los archivos STL que guardan la geometría de las piezas del robot. El archivo generado `robot_description.urdf` esta conformado por 15 *links* (la estructura física del robot) y 14 *joints* (las relaciones entre los componentes), de los cuales 12 son de tipo *fixed* i.e. una conexión rígida, y 2, las llantas, son de tipo *continuous* i.e. permiten una rotación sin límites del ángulo. Además, este archivo contiene las características físicas de los componentes y la referencia a su *mesh* (su archivo STL) y se utiliza como elemento raíz (sistema de referencia) a `base_link` (CLM_Base_2 en SolidWorks). 

Posteriormente se creó el archivo `display.launch.py` el cual llama de forma automática a los tres nodos: `joint_state_publisher`, `robot_state_publisher` y `rviz2`.

### Comandos para ejecución
Primero para descargar paquetes y dependencias:
```
sudo apt update
sudo apt install ros-jazzy-robot-state-publisher \
                 ros-jazzy-joint-state-publisher-gui \
                 ros-jazzy-rviz2 \
```
Para compilar el paquete robot_description:
```
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select robot_description
```
Para cargar el workspace:
```
source install/setup.bash
```
Y, por último, para ejecutar el modelo de ROS2:
```
ros2 launch robot_description display.launch.py
```

### Problemas, soluciones y limitaciones
- Como SolidWorks no es nativo de MacOS, primero se intentó crear el archivo URDF desde CAD Oneshape. Sin embargo, una limitación de este es que los *mates* no se importan directamente. Por lo tanto, se decidió usar una máquina con Windows y SolidWorks.
- Una simplificación que se le hizo al robot fue mantener todos los elementos fijos excepto por las dos ruedas principales. Esto inlcuye a las "ruedas locas" para poder enforcarnos en un solo tipo de movimiento.
- Se buscó solo representar la geometría del robot, no necesariamente cómo se movería y su relación con el motor (un desplazamiento físico).

### Link al video
https://itam2-my.sharepoint.com/personal/tania_dominguez_itam_mx/_layouts/15/stream.aspx?id=%2Fpersonal%2Ftania%5Fdominguez%5Fitam%5Fmx%2FDocuments%2F1%20ITAM%2F11vo%20semestre%2FSeminario%20de%20Titulaci%C3%B3n%2FactividadROSSolid%2FVideoROS%2DSolid%2Emp4&ga=1&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2E2aafc7c3%2Df40c%2D48a9%2Da409%2Da97c622bbd1a
