# pylint: disable=invalid-name

import unittest

from firewheel.control.experiment_graph import (
    Vertex,
    VertexIterator,
    ExperimentGraph,
    NoSuchVertexError,
)


class ExperimentGraphVertexIteratorTestCase(unittest.TestCase):
    def setUp(self):
        self.g = ExperimentGraph()

    def tearDown(self):
        pass

    def test_single_iter(self):
        v1 = Vertex(self.g)

        it = VertexIterator(self.g, [v1.graph_id])

        actual_list = []
        for v in it:
            actual_list.append(v)
        expected_list = [v1]
        self.assertEqual(expected_list, actual_list)

    def test_double_iter(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)

        it = VertexIterator(self.g, [v1.graph_id, v2.graph_id])

        actual_list = []
        for v in it:
            actual_list.append(v)
        expected_list = [v1, v2]
        self.assertEqual(expected_list, actual_list)

    def test_not_in_graph(self):
        it = VertexIterator(self.g, [42])
        with self.assertRaises(NoSuchVertexError):
            next(it)
