from setuptools import find_packages, setup

package_name = 'colmibotbasics'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/play_station_turtle_controller.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='parallels',
    maintainer_email='elenaaslunaap@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'play_station_turtle_controller = colmibotbasics.play_station_turtle_controller:main',
        'colmibot_controller = colmibotbasics.colmibot_controller:main',
    ],
},
)
