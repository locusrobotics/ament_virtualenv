import os

from setuptools import setup
import setuptools.command.install
import ament_virtualenv.install

package_name = 'test_ament_virtualenv'

class InstallCommand(setuptools.command.install.install):
    def run(self):
        super().run()
        scripts_base = os.path.join(self.install_base, "lib/{}".format(package_name))
        ament_virtualenv.install.install_venv(install_base = self.install_base,
                                              package_name = package_name,
                                              scripts_base = scripts_base,
                                              )
        return

setup(
    cmdclass={
        'install': InstallCommand
    },
    name=package_name,
    version='0.0.5',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'requirements.txt']),
        ('lib/' + package_name, ['scripts/main.py'])
    ],
    install_requires=['setuptools'],
    zip_safe=False,
    author='Max Krichenbauer',
    author_email='v-krichenbauer7715@esol.co.jp',
    maintainer='Max Krichenbauer',
    maintainer_email='v-krichenbauer7715@esol.co.jp',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Example of using ament_virtualenv.',
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
)
