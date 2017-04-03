import contextlib
import logging
import sqlite3
import uuid

from idemseq.sequence import SequenceCommand


log = logging.getLogger(__name__)


class StateRegistry(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def update_status(self, command, status):
        """
        Updates status of the command to the specified string.
        
        :param command: SequenceCommand 
        :param status: string 
        :return: None
        """
        raise NotImplementedError()

    def get_status(self, command):
        """
        Returns a string representing the status of the command.
        """
        raise NotImplementedError()

    def get_known_statuses(self):
        """
        Returns a mapping of command names to command statuses for those commands
        for which this registry has information.
        """
        raise NotImplementedError()


class SqliteStateRegistry(StateRegistry):
    _table_name = 'steps'

    def __init__(self, name=None):
        if name is None:
            name = ':memory:'
        super(SqliteStateRegistry, self).__init__(name)
        self._actual_connection = None

    def update_status(self, command, status):
        if status not in SequenceCommand.valid_statuses:
            raise ValueError(status)
        with self._cursor() as cursor:
            cursor.execute('INSERT OR REPLACE INTO {} (name, status) VALUES (?, ?)'.format(
                self._table_name,
            ), (command.name, status))

    def get_status(self, command):
        with self._cursor() as cursor:
            cursor.execute('SELECT status FROM {} WHERE name = ?'.format(
                self._table_name,
            ), (command.name,))
            rows = list(cursor.fetchall())
            if not rows:
                return SequenceCommand.status_unknown
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
            if self.name != ':memory:':
                log.debug('Opening/creating SQLite database at {}'.format(self.name))
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


class DryRunStateRegistry(StateRegistry):
    def __init__(self, name=None):
        # Always generate a unique name to ensure that dry runs aren't related to each other.
        # Dry run state should always be a copy of the last known real state.
        name = '{}-{}'.format(name, uuid.uuid4())
        super(DryRunStateRegistry, self).__init__(name)
        self._storage = {}

    def get_status(self, command):
        return self._storage.get(command.name, SequenceCommand.status_unknown)

    def get_known_statuses(self):
        return self._storage

    def update_status(self, command, status):
        assert status in SequenceCommand.valid_statuses
        self._storage[command.name] = status
