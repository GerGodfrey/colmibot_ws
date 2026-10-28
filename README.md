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
Si aparece vacía la visualización, usar el siguiente comando:
```
LIBGL_ALWAYS_SOFTWARE=1 ros2 launch robot_description display.launch.py
```

### Problemas, soluciones y limitaciones
- Como SolidWorks no es nativo de MacOS, primero se intentó crear el archivo URDF desde CAD Oneshape. Sin embargo, una limitación de este es que los *mates* no se importan directamente. Por lo tanto, se decidió usar una máquina con Windows y SolidWorks.
- Una simplificación que se le hizo al robot fue mantener todos los elementos fijos excepto por las dos ruedas principales. Esto inlcuye a las "ruedas locas" para poder enforcarnos en un solo tipo de movimiento.
- Se buscó solo representar la geometría del robot, no necesariamente cómo se movería y su relación con el motor (un desplazamiento físico).
- Se quitaron muchos de los elementos electrónicos que para la visualización no eran necesarios, dejando solo la estuctura general.

### Link al video
https://itam2-my.sharepoint.com/personal/tania_dominguez_itam_mx/_layouts/15/stream.aspx?id=%2Fpersonal%2Ftania%5Fdominguez%5Fitam%5Fmx%2FDocuments%2F1%20ITAM%2F11vo%20semestre%2FSeminario%20de%20Titulaci%C3%B3n%2FactividadROSSolid%2FVideoROS%2DSolid%2Emp4&ga=1&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2E2aafc7c3%2Df40c%2D48a9%2Da409%2Da97c622bbd1a


## Integración del Colmibot en Gazebo
### Descripción breve
En esta actividad se integró el modelo del Colmibot (paquete `robot_description`) en **Gazebo Harmonic**, un simulador con física (gravedad, fricción, colisiones), para poder moverlo como un robot diferencial. El robot se controla con el mismo joystick comercial y el mismo nodo de la actividad de Turtlesim, conectando sus comandos de velocidad con la simulación mediante `ros_gz_bridge`.

Un mismo archivo URDF sirve para visualizar y para simular: `robot_state_publisher` lo lee y lo publica en el tópico `/robot_description`, junto con la posición de cada pieza en `/tf`. RViz toma esa información para **visualizar** el robot y Gazebo la toma para **simularlo con física**. Las etiquetas `<gazebo>` que se agregaron al final del URDF solo las interpreta Gazebo; RViz las ignora.

### Herramientas
- **Gazebo Harmonic**: simulador de física compatible con ROS 2 Jazzy.
- **ros_gz_sim**: abre Gazebo y crea (*spawn*) el robot en el mundo a partir del URDF.
- **ros_gz_bridge**: puente que traduce tópicos entre ROS 2 y Gazebo, ya que usan sistemas de mensajes distintos.
- **Plugin DiffDrive** (`gz-sim-diff-drive-system`): convierte comandos de velocidad (`Twist`) en el giro de cada llanta.
- **Plugin JointStatePublisher** (`gz-sim-joint-state-publisher-system`): publica el ángulo de las llantas.
- **joy**: lee el control y publica su estado en `/joy`.
- **colmibotbasics**: nuestro nodo de la actividad de Turtlesim, reutilizado sin cambios en su lógica.

### Modificaciones al modelo
Todas se hicieron sobre `robot_description.urdf`.

#### 1. Eje de giro de las llantas
En los dos *joints* `continuous` se cambió `<axis xyz="1 0 0"/>` por `<axis xyz="-1 0 0"/>`.

`<axis>` define alrededor de qué línea gira la llanta y hacia qué lado es el giro positivo, según la **regla de la mano derecha** (el pulgar apunta en la dirección del eje y los dedos indican el sentido positivo). En ROS el robot usa la convención **x hacia adelante, y hacia la izquierda, z hacia arriba**, por lo que para avanzar las llantas deben girar en positivo alrededor de un eje que apunte a la izquierda (+y).

Al calcular la orientación de los ejes exportados desde SolidWorks, ambos apuntaban hacia la derecha (-y). Como el plugin DiffDrive envía velocidad positiva a ambas llantas para avanzar, el robot se movía en reversa. Al invertir el eje, una velocidad positiva hace avanzar al robot. En RViz el único efecto es que el slider gira la llanta en sentido contrario.

#### 2. Fricción
```xml
<gazebo reference="CLM_Llanta60mmD_1"><mu1>1.0</mu1><mu2>1.0</mu2></gazebo>
<gazebo reference="CLM_RuedaLoca_1"><mu1>0.0</mu1><mu2>0.0</mu2></gazebo>
```
`reference` indica la pieza a la que se aplica y `mu1`/`mu2` son los coeficientes de fricción en dos direcciones.
- **Llantas (1.0)**: tienen agarre con el piso; sin fricción patinarían en su lugar.
- **Ruedas locas (0.0)**: en el modelo son fijas (no giran), por lo que con fricción arrastrarían y frenarían al robot. Con fricción cero se deslizan y se comportan como una rueda loca de bola, que rueda en cualquier dirección.

#### 3. Plugin DiffDrive (motor virtual)
Convierte una orden de "avanza a X m/s y gira a Y rad/s" en la velocidad de cada llanta. Con el radio y la separación de las llantas calcula cuánto debe girar cada una: si ambas giran igual el robot avanza recto, y si una gira más rápido que la otra el robot da vuelta.

| Parámetro | Valor | Significado |
|---|---|---|
| `left_joint` / `right_joint` | joints de `CLM_Llanta60mmD_1` / `CLM_Llanta60mmD_2` | Uniones de la llanta izquierda y derecha |
| `wheel_radius` | 0.03 m | Radio de la llanta (60 mm de diámetro) |
| `wheel_separation` | 0.174 m | Distancia entre llantas, medida del CAD |
| `max_linear_velocity` | 0.5 m/s | Límite de avance; el nodo del joystick puede pedir hasta 2 m/s, excesivo para un robot de 20 cm |
| `max_angular_velocity` | 3.0 rad/s | Límite de giro |
| `topic` | `/cmd_vel` | Tópico donde recibe las órdenes de velocidad |
| `odom_topic` | `/odom` | Tópico donde publica la posición estimada del robot |
| `tf_topic`, `frame_id`, `child_frame_id` | `/tf`, `odom`, `base_link` | Publica la transformada `odom → base_link`: dónde está el robot respecto a su punto de partida |

#### 4. Plugin JointStatePublisher
Publica en `/joint_states` cuánto ha girado cada llanta dentro de Gazebo; es lo mismo que hacían los sliders en RViz, pero ahora lo calcula la simulación. Así `robot_state_publisher` conoce el ángulo real de las llantas, lo que permite, por ejemplo, ver el robot en RViz y Gazebo al mismo tiempo.

#### 5. Masas
Se usan las masas e inercias reales exportadas desde el CAD actualizado (aprox. 2.27 kg en total).

#### Archivos agregados
- `config/gz_bridge.yaml`: tópicos que traduce el puente y su dirección.
- `launch/gazebo.launch.py`: arranca todo el sistema.
- Dependencias en `package.xml` (`ros_gz_sim`, `ros_gz_bridge`, `joy`, `colmibotbasics`) y la carpeta `config` en `CMakeLists.txt`.

#### La carpeta `config` y su instalación
`config` es una carpeta nueva para los **archivos de configuración** del paquete (es una convención de ROS). Contiene `gz_bridge.yaml`, la lista de tópicos que el puente traduce entre ROS 2 y Gazebo y en qué dirección.

ROS no usa los archivos de `src/` directamente, sino la copia que `colcon build` deja en `install/`. La siguiente línea de `CMakeLists.txt` indica qué carpetas se copian:
```cmake
install(DIRECTORY urdf meshes launch rviz config
  DESTINATION share/${PROJECT_NAME})
```
```
src/robot_description/              install/robot_description/share/robot_description/
├── urdf/        ──── se copia ───→ ├── urdf/
├── meshes/      ──── se copia ───→ ├── meshes/
├── launch/      ──── se copia ───→ ├── launch/
├── rviz/        ──── se copia ───→ ├── rviz/
└── config/      ──── se copia ───→ └── config/
```
El launch busca el archivo en `install/.../config/gz_bridge.yaml`, por lo que si `config` no está en esa lista el puente no encuentra su configuración. **Regla:** cada carpeta nueva del paquete debe agregarse a esa línea de `CMakeLists.txt` y después recompilar.

### Arquitectura de comunicación
```
Control PS → joy_node → /joy → play_station_turtle_controller → /cmd_vel → ros_gz_bridge → DiffDrive (Gazebo) → llantas
Gazebo → /joint_states, /odom, /tf, /clock → ros_gz_bridge → robot_state_publisher
```
- **Nodos**
  - `joy_node`: publica el estado del control en `/joy`.
  - `play_station_turtle_controller`: convierte los ejes 3 y 4 del control en un mensaje `Twist`. En el launch se redirige su salida de `/turtle1/cmd_vel` a `/cmd_vel` (*remapping*), así que no fue necesario modificar su código.
  - `parameter_bridge` (`ros_gz_bridge`): traduce los tópicos entre ROS 2 y Gazebo.
  - `robot_state_publisher`: publica el URDF en `/robot_description` y calcula las transformadas de cada pieza.
  - `create` (`ros_gz_sim`): lee `/robot_description` y crea el robot en Gazebo.
- **Tópicos**

| Tópico | Tipo (ROS 2) | Dirección | Para qué |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | ROS 2 → Gazebo | Velocidad lineal y angular del robot |
| `/joint_states` | `sensor_msgs/msg/JointState` | Gazebo → ROS 2 | Ángulo de las llantas |
| `/odom` | `nav_msgs/msg/Odometry` | Gazebo → ROS 2 | Posición estimada por el giro de las llantas |
| `/tf` | `tf2_msgs/msg/TFMessage` | Gazebo → ROS 2 | Transformada `odom → base_link` |
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo → ROS 2 | Tiempo de la simulación (`use_sim_time`) |

### Comandos para ejecución
Instalar dependencias (una sola vez):
```
sudo apt update
sudo apt install ros-jazzy-ros-gz ros-jazzy-joy ros-jazzy-teleop-twist-keyboard
```
Compilar el workspace:
```
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```
Ejecutar la simulación con el joystick:
```
LIBGL_ALWAYS_SOFTWARE=1 ros2 launch robot_description gazebo.launch.py
```
El robot se mueve con el stick derecho: arriba/abajo para avanzar o retroceder, izquierda/derecha para girar.

Para probar sin control, en otra terminal (`i` avanza, `j`/`l` gira, `k` detiene):
```
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Problemas, soluciones y limitaciones
- **Error de `colcon build` tras reorganizar el paquete**: al mover `robot_description` de `src/robot_description/robot_description/` a `src/robot_description/`, la compilación fallaba con *"The source directory ... does not exist"* porque `build/` e `install/` guardaban la ruta anterior.
  **Solución:** borrar los archivos generados (`rm -rf build install log`) y volver a compilar.
- **El nodo del joystick no arrancaba en un clon nuevo del repositorio**: al paquete `colmibotbasics` le faltaban `setup.cfg` (indica dónde instalar el ejecutable) y `colmibotbasics/__init__.py` (hace que Python reconozca la carpeta como paquete). Aparecían los errores *"libexec directory does not exist"* y *"No module named colmibotbasics"*.
  **Solución:** se agregaron ambos archivos al repositorio.
- **El robot avanzaba en reversa**: los ejes de las llantas exportados desde SolidWorks apuntaban hacia -y, por lo que una velocidad positiva hacía girar las llantas hacia atrás.
  **Solución:** invertir el eje de ambos *joints* (`<axis xyz="-1 0 0"/>`).
- **El robot no respondía a los comandos (`/cmd_vel` con 0 suscriptores)**: el puente mostraba *"failed to open file ... gz_bridge.yaml"* porque la carpeta `config` no estaba en la línea `install(DIRECTORY ...)` de `CMakeLists.txt` y no se copiaba a `install/`. Además, `colcon build` se ejecutó por error dentro de `src/robot_description/config`, lo que creó carpetas `build/install/log` en el lugar equivocado y no actualizó el workspace.
  **Solución:** agregar `config` a `CMakeLists.txt`, borrar las carpetas generadas dentro de `config` y compilar siempre desde la raíz del workspace.
- **Visualización deficiente en Gazebo dentro de la máquina virtual**: sin tarjeta gráfica real, Gazebo dibuja por software (`LIBGL_ALWAYS_SOFTWARE=1`) y el robot se ve con manchas y sin colores. Al probar el motor gráfico anterior (`--render-engine ogre`), la VM se quedó sin memoria y Gazebo se cerró.
  **Solución:** mantener el motor por defecto; la física y el movimiento no se ven afectados. Se recomienda asignar al menos 6–8 GB de RAM a la VM.
- **Velocidad excesiva del joystick**: el nodo de Turtlesim escala los ejes hasta 2 m/s, demasiado para un robot de 20 cm.
  **Solución:** limitar la velocidad en el plugin DiffDrive (`max_linear_velocity` 0.5 m/s), sin modificar el nodo.

**Limitaciones**
- Las ruedas locas se modelan fijas y con fricción cero en lugar de como esferas que giran; es suficiente para que el robot se desplace, pero no reproduce su comportamiento exacto.
- La odometría (`/odom`) se calcula solo con el giro de las llantas, por lo que acumula error si hay deslizamiento.
- Para usar el control dentro de la VM es necesario conectarlo a la máquina virtual (en VirtualBox: *Devices → USB*).

### Link al video
https://drive.google.com/file/d/1B5EPVo7lPgZjOoeS3nwbClFNNKDlH67F/view?usp=sharing
