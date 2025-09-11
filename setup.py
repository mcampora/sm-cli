from setuptools import setup, find_packages

setup(
    name="smus-setup",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'boto3>=1.26.0',
        'python-dotenv>=0.19.0',
        'click>=8.0.0',
    ],
    entry_points={
        'console_scripts': [
            'smus=smus.cli:main',
        ],
    },
    python_requires='>=3.7',
)
