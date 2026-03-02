from setuptools import find_packages, setup

package_name = 'xr_hand_pipeline'

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
    maintainer='maan',
    maintainer_email='ma3n.he@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
		'hand_ws_publisher = xr_hand_pipeline.hand_ws_publisher:main',
		'hand_pose_subscriber = xr_hand_pipeline.hand_pose_subscriber:main',
        ],
    },
)
