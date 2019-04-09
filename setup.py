import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scarplet",
    version="0.1.4",
    author=["Robert Sare", "George Hilley"],
    author_email="rmsare@stanford.edu",
    description="A Python package for topographic template matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/rmsare/scarplet",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_require=">=3.4",
    install_requires=[
        "numexpr",
        "numpy",
        "matplotlib",
        "gdal",
        "pyfftw",
        "rasterio",
        "scipy"
    ]
)
