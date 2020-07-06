from distutils.core import setup

setup(name = 'stonpy',
    version = '0.1',
    description = 'SBGN to Neo4j database',
    author = 'Adrien Rougny',
    author_email = 'adrienrougny@gmail.com',
    packages = ['stonpy'],
    install_requires = [
        "libsbgnpy",
        "py2neo",
    ],
)
