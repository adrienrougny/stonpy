from distutils.core import setup

setup(
    name="StonPy",
    version="0.2.0",
    description="SBGN to Neo4j database",
    author="Adrien Rougny",
    author_email="adrienrougny@gmail.com",
    packages=["stonpy"],
    include_package_data=True,
    install_requires=[
        "libsbgnpy",
        "py2neo",
        "rdflib",
        "bs4",
        "python-magic",
        "pandas",
        "python-magic-bin; sys_platform == 'win32'",
    ],
    entry_points={
        "console_scripts": [
            "stonpy = stonpy.cli:main",
        ],
    },
)
