from setuptools import setup, find_packages

setup(
    name="homehelper",
    version="1.0.0",
    description="Visuella instruktioner för hushållssysslor",
    author="HomeHelper",
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "homehelper=homehelper.app:main",
        ],
    },
    python_requires=">=3.8",
)
