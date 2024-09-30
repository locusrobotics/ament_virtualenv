from setuptools import find_packages
from setuptools import setup

package_name = 'ament_virtualenv'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=['setuptools'],
    zip_safe=False,
    author='Max Krichenbauer',
    author_email='v-krichenbauer7715@esol.co.jp',
    maintainer='Max Krichenbauer',
    maintainer_email='v-krichenbauer7715@esol.co.jp',
    url='https://github.com/esol-community/ament_virtualenv',
    download_url='https://github.com/esol-community/ament_virtualenv/releases',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Generating a Python virtualenv and installing required packages in it',
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'build_venv = ament_virtualenv.build_venv:main',
            'combine_requirements = ament_virtualenv.combine_requirements:main',
            'glob_requirements = ament_virtualenv.glob_requirements:main',
            'install_venv = ament_virtualenv.install:main',
            'wrap_module = ament_virtualenv.wrap_module:main',
            'wrap_package = ament_virtualenv.wrap_package:main',
        ],
    },
)
