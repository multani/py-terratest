import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()

setuptools.setup(
    name="py-terratest",
    version="0.0.1",
    author="Jonathan Ballet",
    author_email="jon@multani.info",
    description="A Terratest-like test library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/multani/py-terratest",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "boto3",
    ],
    python_requires='>=3.7',
)
