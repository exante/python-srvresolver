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


from typing import Optional, Tuple


class SRVRecord(object):
    '''
    simple srv record implementation for better typing
    '''

    def __init__(self, host: str, port: int, weight: int,
                 priority: int, proto: Optional[str] = None) -> None:
        '''
        srv record class constructor
        :param host: srv record host
        :param port: srv record port
        :param weight: srv record weight
        :param priority: srv record priority
        :param proto: record protocol, optional
        '''
        self.host = host.rstrip('.')
        self.port = port
        self.weight = weight
        self.priority = priority
        self.proto = proto

    @property
    def socket(self) -> Tuple[str, int]:
        '''
        helper for socket library to get pair of host and port
        :return: tuple of (host, port)
        '''
        return (self.host, self.port)

    def __repr__(self) -> str:
        return 'SRVRecord(host={host}, port={port}, weight={weight}, priority={priority})'.format(
            host=self.host,
            port=self.port,
            weight=self.weight,
            priority=self.priority
        )
