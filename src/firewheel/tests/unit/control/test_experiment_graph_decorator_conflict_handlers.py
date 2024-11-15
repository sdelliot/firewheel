# pylint: disable=invalid-name

import unittest

import firewheel.control.experiment_graph
from firewheel.control.experiment_graph import (
    DecoratorConflictError,
    IncorrectConflictHandlerError,
    require_class,
)


class Grandparent:
    def __init__(self):
        pass


@require_class(Grandparent, conflict_handler=lambda a, b, c: None)
class Parent:
    def __init__(self):
        pass

    def common_method(self):
        return 0

    def uncommon_method(self):
        return 2


def raise_handler(entry, _dec_val, _orig_val):
    if entry == "common_method":
        return ChildRaise.common_method
    raise IncorrectConflictHandlerError


def none_handler(entry, _dec_val, _orig_val):
    if entry == "common_method":
        return ChildNone.common_method
    raise IncorrectConflictHandlerError


@require_class(Parent, conflict_handler=raise_handler)
class ChildRaise:
    def __init__(self):
        pass

    def common_method(self):
        return 1


@require_class(Parent, conflict_handler=none_handler)
class ChildRaiseError:
    def __init__(self):
        pass

    def common_method(self):
        return 2

    def uncommon_method(self):
        return 2


@require_class(Parent, conflict_handler=none_handler)
class ChildNone:
    def __init__(self):
        pass

    def common_method(self):
        return 2


@require_class(ChildRaise)
class Grandchild:
    def __init__(self):
        pass


class ExperimentGraphDecoratorConflictHandlersTestCase(unittest.TestCase):
    def setUp(self):
        self.inst = firewheel.control.experiment_graph.ExperimentGraphDecorable()

    def tearDown(self):
        self.inst = None

        # Reset this
        firewheel.control.experiment_graph.CACHED_DECORATOR_OBJECTS = {}

    def test_normal_decorate_order(self):
        self.inst.decorate(Parent)
        self.inst.decorate(ChildRaise)
        self.assertEqual(self.inst.common_method(), 1)

    def test_raise_decorate_order(self):
        self.inst.decorate(Parent)
        with self.assertRaises(DecoratorConflictError):
            self.inst.decorate(ChildRaiseError)

    def test_single_decorate(self):
        self.inst.decorate(ChildRaise)
        self.assertEqual(self.inst.common_method(), 1)

    def test_grandchild(self):
        self.inst.decorate(Grandchild)
        self.assertEqual(self.inst.common_method(), 1)

    def test_parent(self):
        self.inst.decorate(Parent)
        self.assertEqual(self.inst.common_method(), 0)

    def test_normal_decorate_order_none(self):
        self.inst.decorate(Parent)
        self.inst.decorate(ChildNone)
        self.assertEqual(self.inst.common_method(), 2)

    def test_single_decorate_none(self):
        self.inst.decorate(ChildNone)
        self.assertEqual(self.inst.common_method(), 2)

    def test_none_attr_outside_init(self):
        class Base:
            x = 0

        @require_class(Base, conflict_handler=lambda a, b, c: Sub.x)
        class Sub:
            x = None

        try:
            self.inst.decorate(Sub)
            self.fail()
        except firewheel.control.experiment_graph.DecoratorConflictError:
            pass

    def test_none_attr(self):
        class Base:
            def __init__(self):
                self.x = 0

        @require_class(Base, conflict_handler=lambda a, b, c: Sub.x)
        class Sub:
            def __init__(self, x):
                self.x = x

        self.inst.decorate(Base)
        self.inst.decorate(Sub, init_args=[None])
        self.assertEqual(self.inst.x, None)

    def test_val_attr(self):
        class Base:
            def __init__(self):
                self.x = 0

        @require_class(Base, conflict_handler=lambda a, b, c: Sub.x)
        class Sub:
            def __init__(self, x):
                self.x = x

        self.inst.decorate(Base)
        self.inst.decorate(Sub, init_args=[1])
        self.assertEqual(self.inst.x, 1)
