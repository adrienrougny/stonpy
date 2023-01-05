.. _cli:

Command Line Interface
======================

StonPy includes a Command Line Interface (CLI) that allows users to perform all the operations supported by the library directly from the command line.
The CLI is called using the `stonpy` command followed by a subcommand:

.. code-block:: shell

   stonpy <subcommand>

The subcommand may be any of the following:

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Subcommand
     - Description
   * - create
     - To create one or more maps in the database
   * - get
     - To retreive a map from the database
   * - delete
     - To remove a map from the database
   * - query
     - To query the database
   * - delete-all
     - To delete all data from the database
   * - list-repos
     - To list all repositories currently supported

.. _connection:

Connection options
------------------

All of the CLI's subcommands but the `list-repos` subcommand require a connection to a Neo4j database.
These subcommands may be executed with the following connection options:

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Option
     - Description
   * - -a, \--uri
     - The uri for accessing the database
   * - -u, \--user
     - The user name
   * - -p, \--password
     - The password

A subcommand is executed with the connection options as follows:

.. code-block:: shell

   stonpy <subcommand> -a <uri> -u <user> -p <password>

.. _create:

Create
------

The `create` subcommand creates one or more maps in the database from a local or distant file, directory or repository:

.. code-block:: shell

   stonpy create <target>

The `target` argument may be a local path or an url to:

* an SBGN-ML or CellDesigner file;
* a ZIP file or a directory containing any of the above;

or a repository name (see :ref:`repositories`).
A repository is a link to a collection of one or more maps hosted by a third party, that are publicly available and have been published.
StonPy does not contain any of those maps but only the URLs that point to them.

The ID for the created maps are built automatically from their source (generally their path or url) and displayed to `stdout`.

Multiple targets may be specified at once:

.. code-block:: shell

   stonpy create <target1> <target2> <target3>

All data of the database may be deleted before the creation of the maps using the `-d, \--delete-all` option:

.. code-block:: shell

   stonpy create -d <target>

The `create` subsubcommand requires a connection to the database (see :ref:`connection`):

.. code-block:: shell

   stonpy create -a <uri> -u <user> -p <password> <target>

.. _get:

Get
---

The `get` subcommand retreives a map from the database in the SBGN-ML format:

.. code-block:: shell

   stonpy get <map_id>

By default, the content of the map is printed to `stdout`.
The content of the map can be printed to a file instead using the `-o, \--output` option:

.. code-block:: shell

   stonpy get -o <path> <map_id>

The `get` subcommand requires a connection to the database (see :ref:`connection`):

.. code-block:: shell

   stonpy get -a <uri> -u <user> -p <password> <map_id>

.. _delete:

Delete
------

The `delete` subcommand removes a map from the database:

.. code-block:: shell

   stonpy delete <map_id>

The `delete` subcommand requires a connection to the database (see :ref:`connection`):

.. code-block:: shell

   stonpy delete -a <uri> -u <user> -p <password> <map_id>

.. _query:

Query
-----

The `query` subcommand executes a Cypher query against the database and retreives its results:

.. code-block:: shell

   stonpy query <cypher_query>

By default, the results are printed to `stdout`.
The results can be printed to a file instead using the `-o, \--output` option:

.. code-block:: shell

   stonpy query -o <path> <cypher_query>

The results may be converted to valid SBGN-ML maps using the `-c, \--convert` option (see :doc:`/completion_rules` for more details on the completion feature):


.. code-block:: shell

   stonpy query -o <path> -c <cypher_query>

When the conversion option is used, the ouput option (`-o`) described above becomes mandatory.
Additionally, the following options may be used for conversion:

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Option
     - Description
   * - -m, \--unmerge-records
     - Do not merge the results before conversion
   * - -k, \--no-completion
     - Do not complete the results before conversion
   * - -n, \--complete-process-modulations
     - Complete processes with modulations (only if the no completion option (`-k`) described above is not set)
   * - -t, \--to-top-left
     - Translate maps to the top-left corner after conversion

The `query` subcommand requires a connection to the database (see :ref:`connection`):

.. code-block:: shell

   stonpy query -a <uri> -u <user> -p <password> <cypher_query>

.. _delete_all:

Delete all data
---------------

The `delete-all` subcommand deletes all data from the database:

.. code-block:: shell

   stonpy delete-all

The `delete-all` subcommand requires a connection to the database (see :ref:`connection`):

.. code-block:: shell

   stonpy delete-all -a <uri> -u <user> -p <password>


.. _repositories:

List repositories
-----------------

The `list-repos` subcommand lists all available repositories:

.. code-block:: shell

   stonpy list-repos

Currently, the following repositories are supported:

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Repository
     - File(s)
   * - `panther <http://www.pantherdb.org/>`_
     - http://data.pantherdb.org/ftp/pathway/3.6/CD4.1/\*
   * - `acsn <https://acsn.curie.fr/ACSN2/ACSN2.html>`_
     - https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/\*
   * - `acsn_master <https://acsn.curie.fr/ACSN2/ACSN2.html>`_
     - https://acsn.curie.fr/ACSN2/downloads/SBGNMLs/ACSN_denovo_annotations.sbgn
   * - `recon <https://www.ebi.ac.uk/biomodels/MODEL1603150001>`_
     - https://www.vmh.life/files/reconstructions/ReconMaps/ReconMap-2.01.zip
   * - `asthmamap <https://asthma-map.org/>`_
     - https://asthma-map.org/images/af/\*, https://asthma-map.org/images/pd/\*


