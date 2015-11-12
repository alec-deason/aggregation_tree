import unittest

from aggregation_tree import A, Threshold, MeanCombiner

class TestAs(unittest.TestCase):
    def setUp(self):
        self.yes = A(lambda x: True)
        self.no  = ~self.yes

    def test_base_response(self):
        self.assertTrue(self.yes('test'))
        self.assertFalse(self.no('test'))

    def test_or(self):
        a = self.yes | self. no
        self.assertTrue(a('test'))

    def test_and(self):
        a = self.yes & self.no
        self.assertFalse(a('test'))

    def test_negation(self):
        a = ~self.yes
        self.assertFalse(a('test'))

        a = ~self.no
        self.assertTrue(a('test'))

    def test_nesting(self):
        a = (self.yes | self.no) & (self.yes & self.no)
        self.assertFalse(a('test'))

    def test_by_name(self):
        foo = A(lambda x: True, name='FOO')
        bar = A(lambda x: False, name='BAR')
        a = foo | bar
        result = a('test')
        
        foos = result.by_name('FOO')
        self.assertEquals(len(foos), 1)
        self.assertTrue(foos[0])

    def test_sum(self):
        one = A(lambda x: 1)
        a = one + one + one
        result = a('test')
        self.assertEquals(result.result, 3)

    def test_mean(self):
        one = A(lambda x: 1)
        two = A(lambda x: 2)
        a = MeanCombiner([one, two])
        result = a('test')
        self.assertEquals(result.result, 1.5)

    def test_threshold(self):
        e_counter = A(lambda x: len([c for c in x if c == 'e']))
        result = Threshold(e_counter, 3)('test')
        self.assertFalse(result)

        result = Threshold(e_counter, 3)('a very large number of eees')
        self.assertTrue(result)

