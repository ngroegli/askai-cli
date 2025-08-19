from setuptools import setup, find_packages

setup(
    name="askai-cli",
    version="0.1.0",
    package_dir={"": "python"},
    packages=find_packages(where="python") + ["python"],
    python_requires=">=3.7",
    # Add this to make the package available for import
    py_modules=["python"]
)
