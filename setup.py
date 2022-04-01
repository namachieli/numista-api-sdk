import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="numista",
    version="0.1.0",
    author="Namachieli",
    license="MIT",
    description="A Python based SDK for the numista.com api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/namachieli/numista-api-sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 0 - Pre-Alpha",
    ],
    python_requires=">=3.8.10",
    include_package_data=True,
    install_requires=[
        "requests>=2.27.1",
        "iso4217>=1.8.20211001",
        "ruamel.yaml>=0.17.21",
        "validators>=0.18.2",
    ],
)
