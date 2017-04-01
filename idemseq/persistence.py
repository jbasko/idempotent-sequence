import contextlib
import sqlite3

from idemseq.idempotent_sequence import Step


class StepRegistry(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def update_status(self, step, status):
        """
        Updates status of the step to the specified string.
        
        :param step: Step 
        :param status: string 
        :return: None
        """
        raise NotImplementedError()

    def get_status(self, step):
        """
        Returns a string representing the status of the step.
        """
        raise NotImplementedError()

    def get_known_statuses(self):
        """
        Returns a mapping of step names to step statuses for those steps
        for which this registry has information.
        """
        raise NotImplementedError()


class SqliteStepRegistry(StepRegistry):
    _table_name = 'steps'

    def __init__(self, name):
        super(SqliteStepRegistry, self).__init__(name)
        self._actual_connection = None

    def update_status(self, step, status):
        if status not in Step.valid_statuses:
            raise ValueError(status)
        with self._cursor() as cursor:
            cursor.execute('INSERT OR REPLACE INTO {} (name, status) VALUES (?, ?)'.format(
                self._table_name,
            ), (step.name, status))

    def get_status(self, step):
        with self._cursor() as cursor:
            cursor.execute('SELECT status FROM {} WHERE name = ?'.format(
                self._table_name,
            ), (step.name,))
            rows = list(cursor.fetchall())
            if not rows:
                return Step.status_unknown
            else:
                return rows[0][0]

    def get_known_statuses(self):
        with self._cursor() as cursor:
            cursor.execute('SELECT name, status FROM {}'.format(
                self._table_name
            ))
            return {r[0]: r[1] for r in cursor.fetchall()}

    def _ensure_tables_exist(self):
        with self._cursor() as cursor:
            cursor.execute('SELECT * FROM sqlite_master WHERE type = "table";')
            tables = list(cursor.fetchall())
            if not tables:
                cursor.execute('CREATE TABLE {} (name varchar primary key, status varchar);'.format(
                    self._table_name
                ))

    @property
    def _connection(self):
        if self._actual_connection is None:
            self._actual_connection = sqlite3.connect(self.name)
            self._ensure_tables_exist()
        return self._actual_connection

    @contextlib.contextmanager
    def _cursor(self):
        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cursor.close()
