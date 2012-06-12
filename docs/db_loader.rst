
db_loader
=========

Usage
-----

::

    usage: python -m scraptils.db_loader [-h] [-i FILE] [-t {json,csv}] FILE

    Scraptils SQLAlchemy database insert script

    positional arguments:
      FILE                  Sqlalchemy model file (model.py)

    optional arguments:
      -h, --help            show this help message and exit
      -i FILE, --input FILE
                            Input file - default is STDIN
      -t {json,csv}, --input-type {json,csv}
                            Input file type

Examples
--------

::

    $ python -m scraptils.model_insert model.py -i data.json

::

    $ echo '{"_name": "person", "name": "john", "age": 42, "school": {"name": "sch1", "address": "N"}}' | python -m scraptils.db_loader model.py

Module description
------------------

.. automodule:: scraptils.db_loader
   :members:
   :undoc-members:
