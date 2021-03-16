# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os import path


local = path.abspath(path.dirname(__file__))

# README file
with open(path.join(local, 'README.md'), encoding='utf-8') as file:
    readme_file = file.read()

with open(path.join(local, 'LICENSE'), encoding='utf-8') as file:
    license_file = file.read()
    

setup(
    name='STG',
    url='https://github.com/Pbarbecho/STG.git',
    version='1.0',
    description='SUMO Traffic Generator',
    long_description=readme_file,
    long_description_content_type='text/markdown',
    py_modules=['STG'],
    author='Pablo Barbecho',
    author_email='pablo.barbecho@upc.edu',
    keywords='SUMO Traffic Generator',
    packages=find_packages(),
    python_requires='>=3.5',
    install_requires=['click', 'matplotlib', 'numpy ', 'pandas',
                      'pathlib', 'uuid', 'scipy'],
    entry_points={
        'console_scripts': [
            'STG=STG:cli',
        ],
    },
    license="GNU GPL v2",
)
