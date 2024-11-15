# pylint: disable=invalid-name

import unittest

from firewheel.control.experiment_graph import Edge, Vertex, ExperimentGraph


# pylint: disable=comparison-with-itself,unused-variable
class ExperimentGraphEdgeTestCase(unittest.TestCase):
    def setUp(self):
        self.g = ExperimentGraph()

    def tearDown(self):
        pass

    def test_create(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)

        e = Edge(v1, v2)
        self.assertNotEqual(e, None)
        self.assertEqual(e.source, v1)
        self.assertEqual(e.destination, v2)

    def test_different_graph_create(self):
        v1 = Vertex(self.g)
        g2 = ExperimentGraph()
        v2 = Vertex(g2)

        with self.assertRaises(ValueError):
            Edge(v1, v2)

    def test_create_self_cycle(self):
        v1 = Vertex(self.g)
        e = Edge(v1, v1)
        self.assertNotEqual(e, None)
        self.assertEqual(e.source, v1)
        self.assertEqual(e.destination, v1)

    def test_attribute(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e = Edge(v1, v2)
        e["name"] = "test"
        self.assertEqual(e["name"], "test")

    def test_overwrite_attribute(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e = Edge(v1, v2)
        e["name"] = "test"
        self.assertEqual(e["name"], "test")
        e["name"] = "overwritten"
        self.assertEqual(e["name"], "overwritten")

    def test_get_invalid_attribute(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e = Edge(v1, v2)
        with self.assertRaises(KeyError):
            # pylint: disable=pointless-statement
            e["name"]

    def test_has(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e = Edge(v1, v2)
        self.assertFalse("name" in e)
        self.assertFalse(e.has("name"))

        e["name"] = "test"
        self.assertTrue("name" in e)
        self.assertTrue(e.has("name"))

    def test_eq(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)

        e1 = Edge(v1, v2)
        e2 = Edge(v1, v2)
        e3 = Edge(v1, v1)

        self.assertTrue(e1 == e2)
        self.assertFalse(e1 != e2)

        self.assertTrue(e1 is not e3)
        self.assertFalse(e1 is e3)
        self.assertTrue(e2 is not e3)
        self.assertFalse(e2 is e3)

        self.assertIsNotNone(e1)

    def test_same_edge_properties(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)

        e1 = Edge(v1, v2)
        e2 = Edge(v1, v2)

        e1["key"] = "value"
        self.assertEqual(e2["key"], "value")

    def test_delitem(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e1 = Edge(v1, v2)

        e1["foo"] = "bar"
        self.assertEqual(e1["foo"], "bar")

        del e1["foo"]
        with self.assertRaises(KeyError):
            # pylint: disable=pointless-statement
            e1["foo"]

    def test_eq_with_inheritance(self):
        class EdgeSubclass(Edge):
            pass

        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        v3 = Vertex(self.g)
        e1 = EdgeSubclass(v1, v2)
        e2 = EdgeSubclass(v1, v3)

        self.assertTrue(e1 == e1)
        self.assertFalse(e1 == e2)

    def test_delete(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e1 = Edge(v1, v2)

        self.assertEqual(self.g.g.number_of_edges(), 1)

        self.assertEqual(e1.valid, True)
        e1.delete()
        self.assertEqual(self.g.g.number_of_edges(), 0)

        self.assertEqual(e1.valid, False)
        with self.assertRaises(RuntimeError):
            e1.get_object()
        with self.assertRaises(RuntimeError):
            # pylint: disable=unnecessary-dunder-call
            e1.__getitem__(None)
        with self.assertRaises(RuntimeError):
            # pylint: disable=unnecessary-dunder-call
            e1.__setitem__(None, None)
        with self.assertRaises(RuntimeError):
            # pylint: disable=unnecessary-dunder-call
            e1.__delitem__(None)
        with self.assertRaises(RuntimeError):
            e1.has(None)
        with self.assertRaises(RuntimeError):
            # pylint: disable=unnecessary-dunder-call
            e1.__contains__(None)
        with self.assertRaises(RuntimeError):
            # pylint: disable=pointless-statement
            e1 == e1  # noqa: B015
        with self.assertRaises(RuntimeError):
            # pylint: disable=pointless-statement
            e1 != e1  # noqa: B015

    def test_undirected_eq(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)

        e1 = Edge(v1, v2)
        e2 = Edge(v2, v1)

        self.assertTrue(e1 == e1)
        self.assertTrue(e2 == e2)
        self.assertTrue(e1 == e2)

    def test_invalid_source(self):
        v1 = Vertex(self.g)

        with self.assertRaises(TypeError):
            Edge(None, v1)

        v2 = Vertex(self.g)
        v1.delete()
        with self.assertRaises(ValueError):
            Edge(v1, v2)

    def test_invalid_destination(self):
        v1 = Vertex(self.g)

        with self.assertRaises(TypeError):
            Edge(v1, None)

        v2 = Vertex(self.g)
        v2.delete()
        with self.assertRaises(ValueError):
            Edge(v1, v2)

    def test_hash(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        v3 = Vertex(self.g)

        e1 = Edge(v1, v2)
        e2 = Edge(v2, v1)
        e3 = Edge(v1, v3)

        h1 = hash(e1)
        h2 = hash(e2)
        h3 = hash(e3)

        self.assertTrue(e1 == e2)
        self.assertEqual(type(h1), int)
        self.assertEqual(type(h2), int)
        self.assertEqual(h1, h2)

        self.assertFalse(e1 == e3)
        self.assertEqual(type(h3), int)
        self.assertNotEqual(h1, h3)

        g2 = ExperimentGraph()
        v21 = Vertex(g2)
        v22 = Vertex(g2)
        self.assertEqual(v1.graph_id, v21.graph_id)
        self.assertEqual(v2.graph_id, v22.graph_id)
        e212 = Edge(v21, v22)

        h4 = hash(e212)
        self.assertEqual(type(h4), int)
        self.assertNotEqual(h1, h4)
        self.assertNotEqual(h2, h4)
        self.assertNotEqual(h3, h4)

    def test_iter(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e1 = Edge(v1, v2)

        e1["foo"] = 1
        e1["bar"] = 1

        expected_list = ["foo", "bar", "object"]
        expected_list.sort()

        actual_list = []
        for item in e1:
            actual_list.append(item)
        actual_list.sort()

        self.assertEqual(expected_list, actual_list)

    def test_get_object(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        e1 = Edge(v1, v2)

        obj = e1.get_object()
        self.assertEqual(e1, obj)

    def test_find_edge(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        v3 = Vertex(self.g)
        v4 = Vertex(self.g)

        e1 = Edge(v1, v2)
        e2 = Edge(v1, v3)  # noqa: F841
        e3 = Edge(v2, v4)  # noqa: F841

        self.assertEqual(e1, self.g.find_edge(v1, v2))

    def test_find_edge_none(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        v3 = Vertex(self.g)
        v4 = Vertex(self.g)

        e1 = Edge(v1, v2)  # noqa: F841
        e2 = Edge(v1, v3)  # noqa: F841
        e3 = Edge(v2, v4)  # noqa: F841

        self.assertIsNone(self.g.find_edge(v1, v4))

    def test_find_edge_invalid(self):
        v1 = Vertex(self.g)
        v2 = Vertex(self.g)
        v3 = Vertex(self.g)
        v4 = Vertex(self.g)

        e1 = Edge(v1, v2)  # noqa: F841
        e2 = Edge(v1, v3)  # noqa: F841
        e3 = Edge(v2, v4)  # noqa: F841

        self.assertIsNone(self.g.find_edge(v1, "INVALID"))
