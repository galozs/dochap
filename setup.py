from distutils.core import setup
from setuptools import find_packages
import sys
if sys.version_info < (3, 5):
    raise RuntimeError("This package requres Python 3.5+")

setup(
    name='dochap',
    version='1.0.1',
    author='Nitzan Elbaz',
    author_email='elbazni@post.bgu.ac.il',
    packages = ['dochap'],
    url='https://github.com/nitzanel/dochap',
    license='MIT',
    description='do some intresting things with your gtf files',
    long_description='some more info',
    zip_safe=False,
    install_requires=['pathos','dill'],
    python_requires='>=3.5'
)
