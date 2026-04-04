from setuptools import setup, find_packages

setup(
    name="cyberclaw",
    version="1.0.0",
    packages=find_packages(),
    py_modules=["cli"], 
    install_requires=[
        "typer",
        "questionary",
        "rich",
        "python-dotenv",
        "langchain_core"
    ],
    entry_points={
        "console_scripts": [
            "cyberclaw=entry.cli:main",
        ],
    },
)