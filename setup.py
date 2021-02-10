import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mona_uds_client",
    version="0.0.5",
    author="MonaLabs",
    author_email="nemo@monalabs.io",
    description="Client code for python Mona over Unix Domain Socket protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/monalabs/mona-uds-client",
    download_url="http://pypi.python.org/pypi/mona-uds-client/",
    packages=setuptools.find_packages(),
    install_requires=["msgpack>=1.0.2"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
    ],
    python_requires=">=3.7",
)
