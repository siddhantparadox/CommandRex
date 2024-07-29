from setuptools import setup, find_packages

setup(
    name='commandrex',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'anthropic',
        'python-dotenv',
        'spacy',  # Add this line
    ],
    entry_points={
        'console_scripts': [
            'commandrex = commandrex.cli:cli',
            'commandrex-gui = commandrex:gui_main',
        ],
    },
)