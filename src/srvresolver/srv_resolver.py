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
from typing import Iterable, Dict, List, Optional

from srvresolver.srv_record import SRVRecord


class SRVResolver(object):
    '''
    base srv resolver
    '''

    @staticmethod
    def check_port(record: SRVRecord, socket_family: int,
                   socket_type: int, timeout: int = 1) -> bool:
        '''
        check if server and port are available
        :param record: record to check port
        :param socket_family: socket family to be passed to socket constructor
        :param socket_type: socket type to be passed to socket constructor
        :param timeout: socket connection timeout
        :return: true if connection was successful
        '''
        if socket_type == -1:
            socket_type = SRVResolver.guess_socket_type(record.proto)
        with closing(socket.socket(socket_family, socket_type)) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex(record.socket) == 0

    @staticmethod
    def get_highest_priority(records: Iterable[SRVRecord]) -> List[SRVRecord]:
        '''
        get records with highest priority
        :param records: list of srv records
        :return: filtered srv records
        '''
        by_priority = dict()  # type: Dict[int, List[SRVRecord]]
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
            by_weight = by_priority
        else:
            by_weight = list()
            for record in by_priority:
                by_weight.extend([record] * record.weight)

        try:
            return random.choice(by_weight)
        except IndexError:
            return None

    @staticmethod
    def guess_socket_type(proto: Optional[str]) -> int:
        '''
        try to get socket type from srv record
        :param proto: record protocol according to service.proto.<domain> template
        :return: socket type or -1 if unknown protocol
        '''
        if proto in ('tcp', '_tcp'):
            return socket.SOCK_STREAM
        elif proto in ('udp', '_udp'):
            return socket.SOCK_DGRAM
        else:
            return -1

    @staticmethod
    def resolve(address: str) -> List[SRVRecord]:
        '''
        basic srv address resolve method
        :param address: address to resolve
        :return: list of all records from DNS server available for this address
        '''
        records = DNS.query(address, 'SRV')
        proto = records.canonical_name.labels[1].decode('utf8').lstrip('_')
        return [
            SRVRecord(str(srv.target), srv.port,
                      srv.weight, srv.priority, proto)
            for srv in records
        ]

    @staticmethod
    def resolve_active(address: str, socket_family: int = -1,
                       socket_type: int = -1, timeout: int = 1) -> List[SRVRecord]:
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
                    r, socket_family, socket_type, timeout),
                SRVResolver.resolve(address)
            )
        )

    @staticmethod
    def resolve_first(address: str, socket_family: int = -1,
                      socket_type: int = -1, timeout: int = 1) -> Optional[SRVRecord]:
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
                    record, socket_family, socket_type, timeout):
                return record
        return None

    @staticmethod
    def resolve_random(address: str, socket_family: int = -1,
                       socket_type: int = -1, timeout: int = 1) -> Optional[SRVRecord]:
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
