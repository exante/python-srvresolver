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


import dns.resolver as DNS
import random
import socket

from contextlib import closing
from typing import Iterable, List, Optional, Tuple

from srvresolver.srv_record import SRVRecord


class SRVResolver(object):
    '''
    base srv resolver
    '''

    @staticmethod
    def check_port(host: Tuple[str, int], socket_family: int,
                   socket_type: int, timeout: int = 1) -> bool:
        '''
        check if server and port are available
        :param host: socket tuple of (host, port)
        :param socket_family: socket family to be passed to socket constructor
        :param socket_type: socket type to be passed to socket constructor
        :param timeout: socket connection timeout
        :return: true if connection was successful
        '''
        with closing(socket.socket(socket_family, socket_type)) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex(host) == 0

    @staticmethod
    def get_highest_priority(records: Iterable[SRVRecord]) -> List[SRVRecord]:
        '''
        get records with highest priority
        :param records: list of srv records
        :return: filtered srv records
        '''
        by_priority = dict()  # TODO type annotation
        for record in records:
            by_priority.setdefault(record.priority, list()).append(record)

        try:
            # lower priority value means higher record priority
            highest = min(by_priority.keys())
            return by_priority[highest]
        except ValueError:
            # no records found
            return list()

    @staticmethod
    def get_random(records: Iterable[SRVRecord]) -> Optional[SRVRecord]:
        '''
        get random record according to their priority and weight
        :param records: list of srv records
        :return: srv record or null in case if no records found
        '''
        # group by priority first
        by_priority = SRVResolver.get_highest_priority(records)
        # build weighted list
        if all(record.weight == 0 for record in by_priority):
            # special case according to rfc
            by_weight = [record for record in by_priority]
        else:
            by_weight = list()
            for record in by_priority:
                by_weight.extend([record] * record.weight)

        try:
            return random.choice(by_weight)
        except IndexError:
            return None

    @staticmethod
    def resolve(address: str) -> List[SRVRecord]:
        '''
        basic srv address resolve method
        :param address: address to resolve
        :return: list of all records from DNS server available for this address
        '''
        return [
            SRVRecord(str(srv.target), srv.port, srv.weight, srv.priority)
            for srv in DNS.query(address, 'SRV')
        ]

    @staticmethod
    def resolve_active(address: str, socket_family: int = socket.AF_INET,
                       socket_type: int = socket.SOCK_STREAM, timeout: int = 1) -> List[SRVRecord]:
        '''
        resolve srv address and return only records which are available for this address
        :param address: address to resolve
        :param socket_family: socket family to be passed to socket constructor
        :param socket_type: socket type to be passed to socket constructor
        :param timeout: socket connection timeout
        :return: list of records
        '''
        return list(
            filter(
                lambda r: SRVResolver.check_port(
                    r.socket, socket_family, socket_type, timeout),
                SRVResolver.resolve(address)
            )
        )

    @staticmethod
    def resolve_first(address: str, socket_family: int = socket.AF_INET,
                      socket_type: int = socket.SOCK_STREAM, timeout: int = 1) -> Optional[SRVRecord]:
        '''
        quick and dirty resolve srv record and return first available address
        :param address: address to resolve
        :param socket_family: socket family to be passed to socket constructor
        :param socket_type: socket type to be passed to socket constructor
        :param timeout: socket connection timeout
        :return: srv record or null in case if no available records found
        '''
        records = SRVResolver.resolve_active(
            address, socket_family, socket_type, timeout)

        for record in records:
            if SRVResolver.check_port(
                    record.socket, socket_family, socket_type, timeout):
                return record
        return None

    @staticmethod
    def resolve_random(address: str, socket_family: int = socket.AF_INET,
                       socket_type: int = socket.SOCK_STREAM, timeout: int = 1) -> Optional[SRVRecord]:
        '''
        resolve srv address and return random working record according to weight and priority policy
        :param address: address to resolve
        :param socket_family: socket family to be passed to socket constructor
        :param socket_type: socket type to be passed to socket constructor
        :param timeout: socket connection timeout
        :return: srv record or null in case if no available records found
        '''
        records = SRVResolver.resolve_active(
            address, socket_family, socket_type, timeout)

        return SRVResolver.get_random(records)
