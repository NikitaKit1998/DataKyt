import sqlite3
import unittest
import os
import logging
from insert_into_project_table import insert_into_project_table

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d[%(process)d:%(thread)d:%(name)s:%(lineno)d] %(levelname)s %('
                           'message)s',
                    datefmt='%Y-%m-%d %I:%M:%S')


class TestDB(unittest.TestCase):

    @staticmethod
    def create_connection(db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """

        conn = sqlite3.connect(db_file)

        return conn

    @staticmethod
    def create_table(conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        c = conn.cursor()
        c.execute(create_table_sql)

    @staticmethod
    def create_database(path):

        sql_create_projects_table = """ CREATE TABLE project(
                        id SMALLSERIAL  PRIMARY KEY,
                        name text  NOT NULL
                                        );"""

        sql_create_offices_table = """CREATE TABLE office(
                        id SMALLSERIAL  PRIMARY KEY,
                        city text       NOT NULL
                                    );"""

        sql_create_employees_table = """CREATE TABLE employee(
                        id SMALLSERIAL  PRIMARY KEY,
                        name text       NOT NULL,
                        email char(65)  UNIQUE,
                        phone varchar(65) UNIQUE,
                        project_id	SMALLSERIAL CONSTRAINT project_id_fk REFERENCES project (id) ON DELETE CASCADE,
                        office_id	SMALLSERIAL CONSTRAINT office_id_fk REFERENCES office (id)ON DELETE CASCADE
                                         );"""

        sql_create_equipment_type_table = """CREATE TABLE equipment_type(
                                          id          SMALLSERIAL     PRIMARY KEY,
                                          name        text            UNIQUE
                                          );"""

        sql_create_equipment_table = """CREATE TABLE equipment(
                        id                  SMALLSERIAL    PRIMARY KEY,
                        name                text           NOT NULL,
                        warranty            integer        NOT NULL,
                        cost                money          NOT NULL CHECK (cost > 0),
                        status              varchar(10)    NOT NULL
                                CONSTRAINT status_check CHECK(status IN('issued','on reserve','in repair','broken')),
                        description         text,
                        purchase_date       date           NOT NULL,
                        serial_number       varchar(65)    NOT NULL,
                        equipment_type_id	SMALLSERIAL
                                CONSTRAINT equipment_type_id_fk REFERENCES equipment_type(id) ON DELETE CASCADE
                                        );"""

        sql_create_equipment_part_table = """CREATE TABLE equipment_part(
                        id              SMALLSERIAL     PRIMARY KEY,
                        name            text            UNIQUE,
                        equipment_id	SMALLSERIAL
                                CONSTRAINT equipment_id_fk REFERENCES equipment(id) ON DELETE CASCADE
                                        );"""

        sql_create_software_table = """CREATE TABLE software(
                        id      SMALLSERIAL	 PRIMARY KEY,
                        name    text         NOT NULL
                                        );"""

        sql_create_software_license_table = """CREATE TABLE software_license(
                        id                  SMALLSERIAL	PRIMARY KEY,
                        software_id         SMALLSERIAL
                                CONSTRAINT software_id_fk REFERENCES software(id) ON DELETE CASCADE,
                        product_key         text        UNIQUE,
                        date_of_purchase    date        NOT NULL,
                        date_of_expiry	    date        NOT NULL
                                        );"""

        sql_create_employee_sw_license_table = """CREATE TABLE employee_sw_license(
                        id                  SMALLSERIAL 	PRIMARY KEY,
                        date_of_issue       date            NOT NULL,
                        employee_id         SMALLSERIAL
                                CONSTRAINT employee_id_fk REFERENCES employee(id) ON DELETE CASCADE,
                        software_license_id	SMALLSERIAL
                                CONSTRAINT software_license_id_fk REFERENCES software_license(id) ON DELETE CASCADE
                                            );"""
        sql_create_furniture_type_table = """CREATE TABLE furniture_type(
                        id      SMALLSERIAL     PRIMARY KEY,
                        type    text            UNIQUE
                                            );"""

        sql_create_furniture_table = """CREATE TABLE furniture(
                        id                  SMALLSERIAL	PRIMARY KEY,
                        furniture_type_id   SMALLSERIAL
                                CONSTRAINT furniture_type_id_fk REFERENCES furniture_type (id) ON DELETE CASCADE,
                        name                text        NOT NULL,
                        warranty            integer	    NOT NULL,
                        cost                money 	    NOT NULL CHECK (cost > 0)
                                            );"""

        sql_create_employee_furniture_table = """CREATE TABLE employee_furniture(
                        id	            SMALLSERIAL     PRIMARY KEY,
                        date_of_issue   date            NOT NULL,
                        furniture_id    SMALLSERIAL
                                CONSTRAINT furniture_id_fk REFERENCES furniture (id) ON DELETE CASCADE,
                        employee_id	    SMALLSERIAL
                                CONSTRAINT employee_id_fk REFERENCES employee (id) ON DELETE CASCADE
                                            );"""

        sql_create_employee_equipment_table = """CREATE TABLE employee_equipment(
                        id                  SMALLSERIAL     PRIMARY KEY,
                        employee_id         SMALLSERIAL
                                CONSTRAINT employee_id_fk REFERENCES employee(id) ON DELETE CASCADE,
                        equipment_id        SMALLSERIAL
                                CONSTRAINT equipment_id_fk REFERENCES equipment(id) ON DELETE CASCADE,
                        date_of_issue       date            NOT NULL,
                        day_of_return       date
                                            );"""

        sql_table = [sql_create_projects_table, sql_create_offices_table, sql_create_employees_table,
                     sql_create_equipment_type_table, sql_create_equipment_table, sql_create_equipment_part_table,
                     sql_create_software_table, sql_create_software_license_table, sql_create_employee_sw_license_table,
                     sql_create_furniture_type_table, sql_create_furniture_table, sql_create_employee_furniture_table,
                     sql_create_employee_equipment_table]

        # create a database connection
        conn = TestDB.create_connection(path)

        # create table
        for table in sql_table:
            TestDB.create_table(conn, table)

        conn.close()

    @staticmethod
    def take_all_from_table(conn):
        """
        Take all information from project table.
        Parameters
        ----------
        conn: the connection of database.
        """
        cur = conn.cursor()
        cont_of_table = []
        cur.execute('SELECT * FROM project')
        for row in cur:
            cont_of_table.append([row[0], row[1]])
        conn.commit()
        conn.close()

        return cont_of_table

    @staticmethod
    def drop_database(conn, path):

        conn.close()

        os.remove(path)

    def test_db(self):
        """
        Compares array values from csv file and values

        written in the database
        """

        dirname = os.path.dirname(__file__)
        path_to_csv = os.path.join(dirname, 'test_data/test_project.csv')
        path_to_db = os.path.join(dirname, 'test_data/test_database.db')
        TestDB.create_database(path_to_db)
        connection = TestDB.create_connection(path_to_db)
        try:

            elem_of_csv = insert_into_project_table(path_to_csv, connection)

        except Exception as e:
            logger.error(e)
            elem_of_csv = None

        try:
            elem_of_table = TestDB.take_all_from_table(connection)

        except Exception as e:
            logger.error(e)
            elem_of_table = []

        self.assertEqual(elem_of_csv, elem_of_table)
        TestDB.drop_database(connection, path_to_db)


if __name__ == '__main__':
    unittest.main()