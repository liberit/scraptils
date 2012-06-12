
alchemize
=========

Generates SQLAlchemy model from JSON objects

Usage
-----

::

    usage: python -m scraptils.alchemize [-h] [-i FILE] [-t {json,csv}] [-d DB]

    Scraptils JSON SQLizer

    optional arguments:
      -h, --help            show this help message and exit
      -i, --input FILE
                            Input file - default is STDIN
      -t, --input-type {json,csv}
                            Input file type
      -d, --db DB           Database connection string - default is
                            'sqlite:///data.sqlite'


Examples
--------

::

    $ echo '{"_name": "person", "name": "john", "age": 42, "school": {"name": "sch1", "address": "N"}}' | python -m scraptils.sqlize


output::

    from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Table
    from sqlalchemy.orm import relationship, scoped_session, sessionmaker, backref
    from sqlalchemy.ext.declarative import declarative_base

    engine = create_engine('sqlite:///data.sqlite')
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    Base = declarative_base()
    Base.metadata.bind = engine
    Base.query = session.query_property()

    person_school = Table('person_school', Base.metadata
      ,Column('person_id', Integer, ForeignKey('person.id'))
      ,Column('school_id', Integer, ForeignKey('school.id')))

    class Person(Base):
        __tablename__ = 'person'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        age = Column(Integer)
        schools = relationship('School', secondary=person_school)

        def __init__(self, age=None, name=None):
            self.age = age
            self.name = name

    class School(Base):
        __tablename__ = 'school'
        id = Column(Integer, primary_key=True)
        address = Column(String)
        name = Column(String)
        persons = relationship('Person', secondary=person_school)

        def __init__(self, name=None, address=None):
            self.name = name
            self.address = address


    if __name__ == '__main__':
        Base.metadata.create_all(bind=engine)


Module description
------------------

.. automodule:: scraptils.alchemize
   :members:
   :undoc-members:
