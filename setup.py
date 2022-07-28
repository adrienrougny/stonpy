from distutils.core import setup

setup(name = 'stonpy',
    version = '0.1',
    description = 'SBGN to Neo4j database',
    author = 'Adrien Rougny',
    author_email = 'adrienrougny@gmail.com',
    packages = ['stonpy'],
    include_package_data=True,
    install_requires = [
        "libsbgnpy",
        "py2neo",
        "rdflib",
        "bs4",
        "python-magic",
    ],
    entry_points={
        'console_scripts': [
            'stonpy = stonpy.cli:main',
        ],
    },
)
