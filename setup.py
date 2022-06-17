import os.path
import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 6, 1):
    sys.exit("The Vector SDK requires Python 3.6.1 or later")

HERE = os.path.abspath(os.path.dirname(__file__))

VERSION = "0.0.1"


def get_requirements():
    """Load the requirements from requirements.txt into a list"""
    reqs = []
    with open(os.path.join(HERE, "requirements.txt")) as requirements_file:
        for line in requirements_file:
            reqs.append(line.strip())
    return reqs


setup(
    name="pyHAVector",
    version=VERSION,
    description="Customized Anki/Digital Dream Labs SDK",
    url="https://github.com/mtrab/pyhavector",
    author="Malene Trab",
    license="Apache License, Version 2.0",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    zip_safe=True,
    install_requires=get_requirements(),
    extras_require={
        "3dviewer": ["PyOpenGL>=3.1"],
        "docs": ["sphinx", "sphinx_rtd_theme", "sphinx_autodoc_typehints"],
        "experimental": ["keras", "scikit-learn", "scipy", "tensorflow"],
        "test": ["pytest", "requests", "requests_toolbelt"],
    },
)
