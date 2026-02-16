from setuptools import setup

setup(
    name="project-structure-builder",
    version="1.0.0",
    description="Build project structures from text files",
    author="Your Name",
    py_modules=["create_structure"],
    entry_points={
        "console_scripts": [
            "structure=create_structure:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)