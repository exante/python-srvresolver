##########################################################################
# Copyright (c) 2018 EXANTE                                                     #
#                                                                               #
# Permission is hereby granted, free of charge, to any person obtaining a copy  #
# of this software and associated documentation files (the "Software"), to deal #
# in the Software without restriction, including without limitation the rights  #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell     #
# copies of the Software, and to permit persons to whom the Software is         #
# furnished to do so, subject to the following conditions:                      #
#                                                                               #
# The above copyright notice and this permission notice shall be included in    #
# all copies or substantial portions of the Software.                           #
##########################################################################


import psycopg2
import socket

from typing import Optional

from srvresolver.srv_record import SRVRecord
from srvresolver.srv_resolver import SRVResolver


class PostgresResolver(SRVResolver):
    '''
    class helper to resolve postgres srv records
    '''

    def __init__(self, database: str, username: str,
                 password: Optional[str]) -> None:
        '''
        class constructor
        :param database: postgres database
        :param username: postgres username
        :param password: postgres password
        '''
        self.database = database
        self.username = username
        self.password = password

    @staticmethod
    def with_protocol_record(record: SRVRecord, database: str,
                             username: str, password: Optional[str]) -> str:
        '''
        get postgres database record as string
        :param record: postgres instance record in srv
        :param database: postgres database
        :param username: postgres username
        :param password: postgres password
        :return:
        '''
        return 'postgresql://{username}{auth}@{host}:{port}/{database}'.format(
            username=username,
            auth=':' + password if password is not None else '',
            host=record.host,
            port=record.port,
            database=database
        )

    def is_master(self, record: SRVRecord) -> Optional[bool]:
        '''
        check if node on `record` is master
        this function uses `pg_is_in_recovery` call to postgres
        :param record: srv record to check
        :return: true in case if node is master, otherwise false. Returns None in case of exception
        '''
        try:
            with psycopg2.connect(
                    PostgresResolver.with_protocol_record(
                        record, self.database, self.username, self.password)) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT pg_is_in_recovery();')
                    is_slave = cursor.fetchone()[0]
                    return not is_slave
        except Exception:
            return None

    def get_master(self, address: str,
                   socket_family: int = socket.AF_INET) -> Optional[str]:
        '''
        get active master record
        :param address: address to resolve
        :param socket_family: socket family to be passed to socket constructor
        :return: postgres master record if any
        '''
        record = PostgresResolver.get_random(
            filter(
                lambda r: self.is_master(r) is True, # in case of None return
                PostgresResolver.resolve_active(
                    address, socket_family=socket_family, socket_type=socket.SOCK_STREAM)
            )
        )
        if record is not None:
            return PostgresResolver.with_protocol_record(
                record, self.database, self.username, self.password)
        else:
            return None

    def get_slave(self, address: str,
                  socket_family: int = socket.AF_INET) -> Optional[str]:
        '''
        get active slave record
        :param address: address to resolve
        :param socket_family: socket family to be passed to socket constructor
        :return: postgres slave record if any
        '''
        record = PostgresResolver.get_random(
            filter(
                lambda r: self.is_master(r) is False, # in case of None return
                PostgresResolver.resolve_active(
                    address, socket_family=socket_family, socket_type=socket.SOCK_STREAM)
            )
        )
        if record is not None:
            return PostgresResolver.with_protocol_record(
                record, self.database, self.username, self.password)
        else:
            return None
