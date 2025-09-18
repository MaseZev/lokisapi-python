"""
Setup script for LokisApi Python library.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "LokisApi Python Library - A comprehensive Python library for interacting with LokisApi services."

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['requests>=2.25.0']

setup(
    name="lokisapi",
    version="1.0.0",
    author="LokisApi Team",
    author_email="masezev@gmail.com",
    description="A comprehensive Python library for interacting with LokisApi services",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/masezev/lokisapi-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
        "async": [
            "aiohttp>=3.7.0",
        ],
    },
    keywords="lokisapi, openai, gpt, dall-e, ai, machine learning, chat completion, image generation",
    project_urls={
        "Bug Reports": "https://github.com/masezev/lokisapi-python/issues",
        "Source": "https://github.com/masezev/lokisapi-python",
        "Documentation": "https://docs.lokisapi.online",
    },
    include_package_data=True,
    zip_safe=False,
)
