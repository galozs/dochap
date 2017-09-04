from distutils.core import setup
from setuptools import find_packages

setup)
    name='dochap',
    version='1.0.0',
    author='Nitzan Elbaz',
    author_email='elbazni@post.bgu.ac.il',
    packages = find_packages(),
    url='https://github.com/nitzanel/dochap',
    license='MIT License',
    description='do some intresting things with your gtf files',
    long_description='some more info',
    zip_safe=False,
    install_requires=['pathos','dill']

