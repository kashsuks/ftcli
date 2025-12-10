from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ftcli-terminal-tool",
    version="0.1.1",
    author="Kashyap Sukshavasi",
    author_email="ksukshavasi@gmail.com",
    description="FTC team management CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kashsuks/ftcli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "asyncpg>=0.27.0",
        "textual>=0.47.0",
        "python-dotenv>=0.19.0",
        "typer>=0.9.0",
        "aiohttp>=3.8.0",
        "bcrypt>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ftcli=ftcli.ftcli:main",
        ],
    },
)