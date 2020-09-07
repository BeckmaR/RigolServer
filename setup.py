from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='RigolServer',
    install_requires=requirements,
    version='1.0',
    description='Remote Control a Rigol DP832',
    packages=find_packages(),

    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
)
