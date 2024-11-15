# pylint: disable=invalid-name

import random
import unittest

from firewheel.control.experiment_graph import (
    Edge,
    Vertex,
    ExperimentGraph,
    NoSuchVertexError,
)


# pylint: disable=protected-access,unused-variable
class ExperimentGraphTestCase(unittest.TestCase):
    def setUp(self):
        self.g = ExperimentGraph()

    def tearDown(self):
        pass

    def test_add_vertex(self):
        self.assertEqual(self.g.g.number_of_nodes(), 0)
        new_id = self.g._add_vertex()
        self.assertEqual(self.g.g.number_of_nodes(), 1)
        self.assertEqual(self.g.g.nodes[new_id], {})

    def test_add_edge(self):
        self.assertEqual(self.g.g.number_of_nodes(), 0)
        id1 = self.g._add_vertex()
        id2 = self.g._add_vertex()
        self.assertEqual(self.g.g.number_of_nodes(), 2)

        new_edge = (id1, id2)
        self.g._add_edge(id1, id2)
        self.assertEqual(self.g.g.number_of_edges(), 1)
        self.assertEqual(self.g.g.adj[new_edge[0]], {new_edge[1]: {}})

    def test_invalid_source(self):
        self.assertEqual(self.g.g.number_of_nodes(), 0)
        id1 = self.g._add_vertex()
        self.assertEqual(self.g.g.number_of_nodes(), 1)

        with self.assertRaises(NoSuchVertexError):
            self.g._add_edge(42, id1)

    def test_invalid_dest(self):
        self.assertEqual(self.g.g.number_of_nodes(), 0)
        id1 = self.g._add_vertex()
        self.assertEqual(self.g.g.number_of_nodes(), 1)

        with self.assertRaises(NoSuchVertexError):
            self.g._add_edge(id1, 42)

    def test_get_vertices(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)

        actual_list = []
        for v in self.g.get_vertices():
            actual_list.append(v)
        expected_list = [v1, v2]

        self.assertEqual(expected_list, actual_list)

    def test_find_vertex(self):
        name = "TEST"
        v1 = Vertex(self.g)
        v1.name = name
        v2 = Vertex(self.g)
        v2.name = "v2"

        self.assertEqual(v1, self.g.find_vertex(name))

    def test_find_vertex_none(self):
        name = "TEST"
        v1 = Vertex(self.g)  # noqa: F841
        v2 = Vertex(self.g)  # noqa: F841

        self.assertIsNone(self.g.find_vertex(name))

    def test_find_vertex_by_id(self):
        name = "TEST"
        v1 = Vertex(self.g)
        v1.name = name
        v2 = Vertex(self.g)
        v2.name = "v2"
        self.assertEqual(v1, self.g.find_vertex_by_id(v1.graph_id))

    def test_find_vertex_by_invalid_id_str(self):
        name = "TEST"
        v1 = Vertex(self.g)
        v1.name = name
        v2 = Vertex(self.g)
        v2.name = "v2"
        self.assertIsNone(self.g.find_vertex_by_id("invalid"))

    def test_find_vertex_by_invalid_id(self):
        name = "TEST"
        v1 = Vertex(self.g)
        v1.name = name
        v2 = Vertex(self.g)
        v2.name = "v2"
        self.assertIsNone(self.g.find_vertex_by_id(50))

    def test_unique_graph_id_single(self):
        # Add several vertexs
        v1 = Vertex(self.g)
        v1.name = "v1"
        v2 = Vertex(self.g)
        v2.name = "v2"
        v3 = Vertex(self.g)
        v3.name = "v3"
        v4 = Vertex(self.g)
        v4.name = "v4"
        v5 = Vertex(self.g)
        v5.name = "v5"
        v6 = Vertex(self.g)
        v6.name = "v6"

        # Delete some
        v1.delete()
        v2.delete()
        v3.delete()

        # Add new vertex
        v7 = Vertex(self.g)
        v7.name = "v7"

        self.assertNotEqual(v7.graph_id, v4.graph_id)
        self.assertNotEqual(v7.graph_id, v5.graph_id)
        self.assertNotEqual(v7.graph_id, v6.graph_id)

    def test_unique_graph_id_multiple(self):
        # Add several vertexs
        v1 = Vertex(self.g)
        v1.name = "v1"
        v2 = Vertex(self.g)
        v2.name = "v2"
        v3 = Vertex(self.g)
        v3.name = "v3"
        v4 = Vertex(self.g)
        v4.name = "v4"
        v5 = Vertex(self.g)
        v5.name = "v5"
        v6 = Vertex(self.g)
        v6.name = "v6"

        # Delete some
        v1.delete()
        v2.delete()
        v3.delete()

        # Add new vertex
        v7 = Vertex(self.g)
        v7.name = "v7"
        self.assertNotEqual(v7.graph_id, v4.graph_id)
        self.assertNotEqual(v7.graph_id, v5.graph_id)
        self.assertNotEqual(v7.graph_id, v6.graph_id)

        v8 = Vertex(self.g)
        v8.name = "v8"
        self.assertNotEqual(v8.graph_id, v4.graph_id)
        self.assertNotEqual(v8.graph_id, v5.graph_id)
        self.assertNotEqual(v8.graph_id, v6.graph_id)
        self.assertNotEqual(v8.graph_id, v7.graph_id)

        v9 = Vertex(self.g)
        v9.name = "v9"
        self.assertNotEqual(v9.graph_id, v4.graph_id)
        self.assertNotEqual(v9.graph_id, v5.graph_id)
        self.assertNotEqual(v9.graph_id, v6.graph_id)
        self.assertNotEqual(v9.graph_id, v7.graph_id)
        self.assertNotEqual(v9.graph_id, v8.graph_id)

        v10 = Vertex(self.g)
        v10.name = "v10"
        self.assertNotEqual(v10.graph_id, v4.graph_id)
        self.assertNotEqual(v10.graph_id, v5.graph_id)
        self.assertNotEqual(v10.graph_id, v6.graph_id)
        self.assertNotEqual(v10.graph_id, v7.graph_id)
        self.assertNotEqual(v10.graph_id, v8.graph_id)
        self.assertNotEqual(v10.graph_id, v9.graph_id)

    # pylint: disable=unused-argument
    def test_single_proc_all_pairs_shortest_path(self):
        v1 = Vertex(self.g)
        v1.name = "v1"
        v2 = Vertex(self.g)
        v2.name = "v2"
        v3 = Vertex(self.g)
        v3.name = "v3"
        e1 = Edge(v1, v2)  # noqa: F841
        e2 = Edge(v2, v3)  # noqa: F841

        def vfilter(vertex):
            if vertex.name != "v2":
                return True
            return False

        def action(source, dest, path):
            self.assertNotEqual(source.name, "v2")
            self.assertNotEqual(dest.name, "v2")

        self.g._single_process_all_pairs_shortest_path(vfilter, action)

    # pylint: disable=unused-argument
    def test_filtered_all_pairs_shortest_path_no_workers(self):
        v1 = Vertex(self.g)
        v1.name = "v1"
        v2 = Vertex(self.g)
        v2.name = "v2"
        v3 = Vertex(self.g)
        v3.name = "v3"
        e1 = Edge(v1, v2)  # noqa: F841
        e2 = Edge(v2, v3)  # noqa: F841

        def vfilter(vertex):
            if vertex.name != "v2":
                return True
            return False

        def action(source, dest, path):
            self.assertNotEqual(source.name, "v2")
            self.assertNotEqual(dest.name, "v2")

        self.g.filtered_all_pairs_shortest_path(
            vertex_filter=vfilter, path_action=action, num_workers=0
        )

    # pylint: disable=unused-argument
    def test_filtered_all_pairs_shortest_path_one_worker(self):
        v1 = Vertex(self.g)
        v1.name = "v1"
        v2 = Vertex(self.g)
        v2.name = "v2"
        v3 = Vertex(self.g)
        v3.name = "v3"
        e1 = Edge(v1, v2)  # noqa: F841
        e2 = Edge(v2, v3)  # noqa: F841

        def vfilter(vertex):
            if vertex.name != "v2":
                return True
            return False

        def action(source, dest, path):
            self.assertNotEqual(source.name, "v2")
            self.assertNotEqual(dest.name, "v2")

        self.g.filtered_all_pairs_shortest_path(
            vertex_filter=vfilter, path_action=action, num_workers=1
        )

    # pylint: disable=unused-argument
    def test_sample_filtered_all_pairs_shortest_path_one_worker(self):
        """
        We start by making a complete graph of size 5. We choose a specific
        seed that will result in only the first two vertices being selected
        for single source shortest paths.
        We verify that none of the found edges start from the remaining vertices.
        """
        vertices = []
        for v in range(5):
            vertex = Vertex(self.g)
            vertex.name = v
            vertices.append(vertex)
        edges = []
        for u in vertices:
            for v in vertices:
                if u.name == v.name:
                    continue

                e = Edge(u, v)
                edges.append(e)

        def action(source, dest, path):
            if source.name in (2, 3, 4):
                raise RuntimeError("source.name equals 2, 3, or 4.")

        random.seed(82)  # noqa: DUO102

        def vfilter(x):
            return True

        self.g.filtered_all_pairs_shortest_path(
            vertex_filter=vfilter, path_action=action, num_workers=1, sample_pct=0.5
        )
