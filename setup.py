#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from setuptools import setup, find_packages

__version__ = re.findall(
    r"""__version__ = ["']+([0-9\.]*)["']+""", open("af_opt/__init__.py").read()
)[0]

setup(
    name="Airfoil Optimizer",
    version=__version__,
    description="Airfoil Optimization using OpenMDAO",
    author="Daniel de Vries",
    author_email="danieldevries6@gmail.com",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.17",
        "openmdao<2.10,>=2.8",
        "h5py<3,>=2.10.0",
        "cst<2,>=1.0.1",
        "differential_evolution<2,>=1.7.0",
        "matplotlib<4,>=3",
    ],
    url="https://github.com/daniel-de-vries/airfoil-optimizer",
    download_url="https://github.com/daniel-de-vries/airfoil-optimizer/archive/v{0}.tar.gz".format(
        __version__
    ),
    keywords=["airfoil", "optimization"],
    license="MIT License",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
    ],
)
