from setuptools import setup, find_packages 

setup(
    name = "taxipred",
    version = "0.0.1",
    description = "This package contains taxipred app which will predict taxi prices",
    author = "Caroline",
    author_email= "author@email.com",
    install_requires = ["streamlit", "pandas", "fastapi", "scikit-learn", "uvicorn"],
    package_dir = {"": "src"},
    package_data = {"taxipred": ["data/*.csv"]},
    packages = find_packages()
)

