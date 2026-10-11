from setuptools import find_packages, setup

package_name = 'turing_drive'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='D500 sensor model and test driving node for the Turing Track simulator',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': ['drive_test = turing_drive.drive_test:main', 'd500_relay = turing_drive.d500_relay:main',
        ],
    },
)
