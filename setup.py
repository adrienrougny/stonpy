from distutils.core import setup

setup(name = 'ston',
    version = '2.0',
    description = 'SBGN to Neo4j database',
    author = 'Adrien Rougny',
    author_email = 'rougny.adrien@aist.go.jp',
    packages = ['ston'],
    install_requires = [
        "libsbgnpy",
        "py2neo",
    ],
)
