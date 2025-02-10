import sys
from setuptools import setup, find_packages

setup(
    name="spanish-flashcard-builder",
    version="0.1.0",
    description="A tool for building and managing Spanish vocabulary flashcards",
    author="Bryson Thill",
    packages=["spanish_flashcard_builder"],
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.26.0",
        "python-dotenv>=0.19.0",
        "openai>=0.27.0",
        "pillow>=9.0.0",
        "tqdm>=4.62.0",
        "spacy>=3.0.0",
        "click>=8.0.0",
        "pyyaml>=5.1",
    ],
    entry_points={
        'console_scripts': [
            'spanish-flashcard-builder=spanish_flashcard_builder.cli:main',
            'sfb=spanish_flashcard_builder.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Topic :: Education",
        "Natural Language :: Spanish",
        "License :: OSI Approved :: MIT License"
    ],
) 