# pylint: disable=invalid-name

import unittest

import networkx as nx

from firewheel.control.experiment_graph import (
    Edge,
    Vertex,
    EdgeIterator,
    ExperimentGraph,
    NoSuchVertexError,
)


class ExperimentGraphEdgeIteratorTestCase(unittest.TestCase):
    def setUp(self):
        self.g = ExperimentGraph()

    def tearDown(self):
        pass

    def test_single_iter(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e1 = Edge(v1, v2)

        it = EdgeIterator(self.g, [v1.graph_id])

        actual_list = []
        for e in it:
            actual_list.append(e)
        expected_list = [e1]
        self.assertEqual(expected_list, actual_list)

    def test_multiple_iter(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        v3 = Vertex(self.g)

        e1 = Edge(v1, v2)
        e2 = Edge(v1, v3)
        e3 = Edge(v2, v3)

        it = EdgeIterator(self.g, [v1.graph_id, v2.graph_id])

        actual_list = []
        for e in it:
            actual_list.append(e)
        expected_list = [e1, e2, e3]
        self.assertEqual(len(expected_list), len(actual_list))
        self.assertEqual(expected_list, actual_list)

    def test_duplicate_iter(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e1 = Edge(v1, v2)

        it = EdgeIterator(self.g, [v1.graph_id, v1.graph_id])
        actual_list = []
        for e in it:
            actual_list.append(e)
        expected_list = [e1]
        self.assertEqual(len(actual_list), 1)
        self.assertEqual(expected_list, actual_list)

    def test_not_in_graph(self):
        with self.assertRaises(NoSuchVertexError):
            EdgeIterator(self.g, [42])

    def test_get_edges(self):
        self.assertEqual(self.g.g.number_of_nodes(), 0)
        id1 = Vertex(self.g)
        id2 = Vertex(self.g)
        self.assertEqual(self.g.g.number_of_nodes(), 2)

        new_edge = Edge(id1, id2)
        self.assertEqual(self.g.g.number_of_edges(), 1)

        actual_list = []
        for e in self.g.get_edges():
            actual_list.append(e)

        expected_list = [new_edge]
        self.assertEqual(expected_list, actual_list)

    def test_large_graph(self):
        # The iterator would previously fail when the graph contained
        # hundreds of thousands of edges. Reproduce that condition.
        # This ends up being a torture test for improper recursion in the
        # iterator.
        self.g.g = nx.complete_graph(1000)
        # Patch up our new graph to be close-enough to a real experiment graph
        # in internal structure.
        for v in self.g.g.nodes:
            self.g.g.nodes[v]["object"] = v
        for e1 in self.g.g.adj:
            for e2 in self.g.g.adj[e1]:
                self.g.g.adj[e1][e2]["object"] = (e1, e2)

        total_edge_count = nx.number_of_edges(self.g.g)

        eit = EdgeIterator(self.g, self.g.g.nodes())
        counter = 0
        for _ in eit:
            counter += 1

        self.assertEqual(total_edge_count, counter)

    def test_omit_edge(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        v3 = Vertex(self.g)

        e1 = Edge(v1, v2)
        e2 = Edge(v1, v3)
        # pylint: disable=unused-variable
        e3 = Edge(v2, v3)  # noqa: F841

        it = EdgeIterator(self.g, [v1.graph_id])

        actual_list = []
        for e in it:
            actual_list.append(e)
        expected_list = [e1, e2]
        self.assertEqual(len(expected_list), len(actual_list))
        self.assertEqual(expected_list, actual_list)
