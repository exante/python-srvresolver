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


import unittest

from srvresolver.srv_record import SRVRecord
from srvresolver.srv_resolver import SRVResolver


valid_srv_record = SRVRecord('httpbin.org', 80, 1, 1, 'tcp')
invalid_srv_record = SRVRecord('httpbin.org', 666, 1, 1, 'tcp')

srv_records_with_one_highest_priority = [
    valid_srv_record,
    SRVRecord('httpbin.org', 80, 1, 10, 'tcp'),
    SRVRecord('httpbin.org', 80, 1, 10, 'tcp')
]

srv_records_with_two_highest_priority = [
    valid_srv_record,
    invalid_srv_record,
    SRVRecord('httpbin.org', 80, 1, 10, 'tcp')
]

srv_records_with_same_priority = [valid_srv_record] * 3 + [invalid_srv_record]

cycle_count = 10
srv_records_with_different_weights = {
    0: SRVRecord('httpbin.org', 80, 0, 1, 'tcp'),
    100: SRVRecord('httpbin.org', 80, 100, 1, 'tcp'),
    200: SRVRecord('httpbin.org', 80, 200, 1, 'tcp'),
    300: SRVRecord('httpbin.org', 80, 300, 1, 'tcp'),
    400: SRVRecord('httpbin.org', 80, 400, 1, 'tcp'),
    500: SRVRecord('httpbin.org', 80, 500, 1, 'tcp')
}


class SRVResolverTestCase(unittest.TestCase):

    def test_check_port(self):
        self.assertEqual(SRVResolver.check_port(valid_srv_record, -1, -1, 1), True)
        self.assertEqual(SRVResolver.check_port(invalid_srv_record, -1, -1, 1), False)

    def test_get_highest_priority(self):
        result = SRVResolver.get_highest_priority(srv_records_with_one_highest_priority)
        self.assertEqual(result, [valid_srv_record])

    def test_get_random(self):
        result = SRVResolver.get_random(srv_records_with_two_highest_priority)
        self.assertIn(result, [valid_srv_record, invalid_srv_record])
        result = SRVResolver.get_random(srv_records_with_same_priority)
        self.assertIn(result, srv_records_with_same_priority)

    def test_get_random_with_weight(self):
        total_weight = sum(srv_records_with_different_weights.keys())
        random_weights = dict()
        for _ in range(total_weight * cycle_count):
            result = SRVResolver.get_random(srv_records_with_different_weights.values())
            random_weights.setdefault(result.weight, 0)
            random_weights[result.weight] += 1
        self.assertEqual(random_weights.get(0, 0), 0)
        for weight, count in random_weights.items():
            self.assertAlmostEqual(count / (total_weight * cycle_count), weight / total_weight, delta=0.1)


if __name__ == '__main__':
    unittest.main()
