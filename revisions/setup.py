from setuptools import setup, find_packages

setup(
    name="repokit",
    version="0.1.0",
    description="Repository Template Generator",
    author="Your Name",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'repokit=cli:main',
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
