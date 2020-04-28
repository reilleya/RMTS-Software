from setuptools import setup, find_packages

try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    print('pyqt_distutils not found, build_ui command will be unavailable')
    build_ui = None  # user won't have pyqt_distutils when deploying
    cmdclass = {}

setup(
    name='RMTSI',
    version='0.1.0',
    license='GPLv3',
    packages=find_packages(),
    url='https://github.com/reilleya/RMTS-Software',
    description='Software to interface with the RMTS board over radio link',
    cmdclass=cmdclass
)