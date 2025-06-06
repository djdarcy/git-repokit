import os
from setuptools import setup, find_packages

# Read version from __version__.py
version = {}
with open(os.path.join("repokit", "__version__.py")) as f:
    exec(f.read(), version)

setup(
    name="repokit",
    version=version["__version__"],
    description="Repository Template Generator",
    author="Dustin Darcy",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        'dev': [
            'python-dotenv>=0.19.0',
            'requests>=2.25.0',
            'pytest>=6.0.0',
            'coverage>=5.0.0',
        ],
        'test': [
            'python-dotenv>=0.19.0',
            'requests>=2.25.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'repokit=repokit.cli:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control :: Git',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
