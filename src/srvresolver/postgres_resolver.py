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
from srvresolver.srv_resolver_cached import SRVResolverCached


class PostgresResolver(SRVResolverCached):

    @staticmethod
    def is_master(record: SRVRecord, username: str,
                  password: Optional[str]) -> Optional[bool]:
        '''
        check if node on `record` is master
        this function uses `pg_is_in_recovery` call to postgres
        :param record: srv record to check
        :param username: postgres username
        :param password: postgres password
        :return: true in case if node is master, otherwise false. Returns None in case of exception
        '''
        try:
            with psycopg2.connect(
                    dbname='postgres', user=username, password=password,
                    host=record.host, port=record.port) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT * FROM pg_replication_slots;')
                    if cursor.fetchone() is None:
                        cursor.execute('SELECT pg_is_in_recovery();')
                        return not cursor.fetchone()[0]
                    else:
                        cursor.execute('SELECT * from pg_replication_slots WHERE active_pid IS NOT NULL;')
                        return cursor.fetchone() is not None
        except Exception:
            return None

    @staticmethod
    def get_master(address: str, username: str, password: Optional[str],
                   socket_family: int = socket.AF_INET) -> Optional[SRVRecord]:
        '''
        get active master record
        :param address: address to resolve
        :param username: postgres username
        :param password: postgres password
        :param socket_family: socket family to be passed to socket constructor
        :return: postgres master record if any
        '''
        return PostgresResolver.get_random(
            filter(
                # in case of None return
                lambda r: PostgresResolver.is_master(
                    r, username, password) is True,
                PostgresResolver.resolve_active(
                    address, socket_family=socket_family)
            )
        )

    @staticmethod
    def get_slave(address: str, username: str, password: Optional[str],
                  socket_family: int = socket.AF_INET) -> Optional[SRVRecord]:
        '''
        get active slave record
        :param address: address to resolve
        :param username: postgres username
        :param password: postgres password
        :param socket_family: socket family to be passed to socket constructor
        :return: postgres slave record if any
        '''
        return PostgresResolver.get_random(
            filter(
                # in case of None return
                lambda r: PostgresResolver.is_master(
                    r, username, password) is False,
                PostgresResolver.resolve_active(
                    address, socket_family=socket_family)
            )
        )
