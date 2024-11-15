*****************
Adding Complexity
*****************

Now that we have *mostly* accomplished our primary objective and built a topology with a hardened firewall, we need to implement the firewall rules to protect our data center.
Recall that we initially determined that two model components would be useful, where the first would provide the topology (i.e., :ref:`acme-topology`) and the second would add firewall rules.
In this module, you will use your previously learned skills to create this second model component.
Along the way, we will provide minimal hints.
Here are the general steps:

1. Create a new model component called ``acme.firewall`` ensuring correct dependencies.
2. Create a Plugin in ``acme.firewall`` to change the firewall rules to block all traffic to the data center except for *Building 2* residents.
3. Test your experiment.
4. Identify other ways in which your experiment could be improved.


Creating a new Model Component
==============================

**Questions to answer**:

* What CLI command was used to create a template for a new model component?
* What are the MC's dependencies?
* Do we need a plugin file?

.. dropdown:: Hint #1

    We can use the :ref:`helper_mc_generate` command to create the skeleton of our new model component.

.. dropdown:: Hint #2

    We will need a plugin file which will modify any :py:class:`vyos.helium118.Helium118` router with a specific name (e.g. "firewall.acme.com").

.. dropdown:: Possible Solution

    In order to create the skeleton for our new model component, run the following:

    .. code-block:: bash

        $ firewheel mc generate

        (name) ModelComponent name : acme.firewall
        (attribute_depends) (space-separated-strings) Graph Attribute(s) depended on by the new ModelComponent []: topology
        (attribute_provides) (space-separated-strings) Graph Attribute(s) provided by the new ModelComponent []:
        (attribute_precedes) (space-separated-strings) Graph Attribute(s) preceded by the new ModelComponent []:
        (model_component_depends) (space-separated-strings) ModelComponent(s) required by name []: vyos.helium118
        (model_component_precedes) (space-separated-strings) ModelComponent(s) that will be preceded by name []:
        (plugin) File for a plugin []: plugin.py
        (model_component_objects) File for Model Component Objects []:
        (location) Location for the new ModelComponent : acme/firewall
        (vm_resources) (space-separated-strings) File(s) to be used as a vm_resource []:
        (image) File to be used as a VM disk []:
        (arch) Architecture for specified image []:


Updating our Plugin
===================

In this section, you will begin to understand that in order to create a model you first need to deeply understand the system you are modeling.
Without this system understanding, Emulytics models lose fidelity and value.

**Questions to answer**:

* How do firewall rules work in VyOS?
* How can all traffic to the data center be blocked?
* What imports are needed?
* How can I search the graph for the firewall VM?
* Are there existing methods to help set VyOS firewall rules?

.. dropdown:: Hint #1 (firewall rules)

    `This link <https://www.google.com/search?q=how+do+firewall+rules+work+in+vyos>`_ will be helpful in understanding VyOS firewall rules.

.. dropdown:: Hint #2 (firewall rules)

    You will need to define a rule-group, specify a ``default-action``, define a new rule and the rule's action.

    .. dropdown:: Hint #2.1

        .. code-block:: bash

            # set firewall name <name> description <text>
            # set firewall name <name> default-action [drop | reject | accept]
            # set firewall name <name> rule <1-999999> source address [address | addressrange | CIDR]
            # set firewall name <name> rule 1 action [drop | reject | accept]
            # set interface ethernet <ethN> firewall [in | out | local] [name | ipv6-name] <rule-set>

        With the options selected it should look akin to:

        .. code-block:: bash

            set firewall name drop_datacenter description "Dropping traffic destined for the data center"
            set firewall name drop_datacenter default-action accept
            set firewall name drop_datacenter rule 1 destination address 10.0.5.0/24
            set firewall name drop_datacenter rule 1 action drop
            set interface ethernet eth1 firewall in name drop_datacenter

.. dropdown:: Hint #3 (imports)

    We will need a plugin file which will modify the :py:class:`vyos.helium118.Helium118` router with a specific name (e.g. "firewall.acme.com").
    In order to identify the routers, you will likely need to import the object.

.. dropdown:: Hint #4 (searching the Graph)

    See :py:meth:`find_vertex() <firewheel.control.experiment_graph.ExperimentGraph.find_vertex>` and :py:meth:`get_vertices() <firewheel.control.experiment_graph.ExperimentGraph.get_vertices>`.


.. dropdown:: Hint #5 (VyOS configuration)

    There is an :py:meth:`assign_firewall_policies() <vyos.VyOSRouter.assign_firewall_policies>` method which will help.

    .. dropdown:: Hint #5.1

        To make configuring VyOS easier, there is a :py:class:`vyos.VyOSConfiguration` object which is comprised of :py:class:`vyos.VyOSConfigItems`.
        These :py:class:`vyos.VyOSConfigItems` are constructed in a tree-like structure to
        minimize duplication of VyOS CLI configuration.
        For example, the rules used in this model can be described with the following graph:

        .. graphviz::

            digraph firewall_rule {
                "name drop_datacenter" -> "default-action accept";
                "name drop_datacenter" -> "rule 1";
                "rule 1" -> "destination";
                "destination" -> "address 10.0.5.0/24"
                "rule 1" -> "action drop";
            }

        Using this graph-like structure, the :ref:`vyos_mc` model component will convert the entire configuration into proper VyOS configuration syntax.

    .. dropdown:: Hint #5.2

        Wrapping your head around the :py:class:`vyos.VyOSConfiguration` system is challenging (feel free to submit a PR to improve it!) so try to not get discouraged if it is confusing.
        Here is what we came up with as the parameter to pass into the :py:meth:`assign_firewall_policies() <vyos.VyOSRouter.assign_firewall_policies>` method.

        .. code-block:: python

            # Create the initial rule-group
            rule = VyOSConfigItem("name", "drop_datacenter")

            # Add our default action
            rule.add_children(VyOSConfigItem("default-action", "accept"))

            # Create rule 1
            rule.add_children(VyOSConfigItem("rule", "1"))

            # Let's get the rule VyOSConfigItem so that we can append to its tree
            rule_1 = rule.find("rule")

            dest = VyOSConfigItem("destination")

            # We programmatically found the right address just like you did...right!?
            # because hardcoding may lead to unexpected errors if the topology changes.
            dest.add_children(VyOSConfigItem("address", f"{dc_net}"))

            # Adding the destination and action to "rule 1"
            rule_1.add_children(dest)
            rule_1.add_children(VyOSConfigItem("action", "drop"))

            # Add the new firewall policy
            vert.assign_firewall_policies({"in": [rule]})

.. dropdown:: Hint #6

    It's important to programmatically identify the network for the data center.
    This can easily be done as we know the data center has two networks and one of them is also connected to the firewall.

    Using one of the methods from Hint #4, we can identify the data center router and extract it's networks.
    The :py:class:`base_objects.Interfaces` object contains all the network interface information for a VM. We can iterate over the existing interfaces and extract the network as each interface is a dictionary with the relevant information.

    .. dropdown:: Hint #6.1

        Okay, I guess you can have some code:

        .. code-block:: python

            # Now we can find the non-overlapping network
            data_center_router = self.g.find_vertex("datacenter.acme.com")
            nets = set()
            for interface in vert.interfaces.interfaces:
                nets.add(str(interface["network"]))

            # Now we can find the non-overlapping network
            for interface in data_center_router.interfaces.interfaces:
                if str(interface["network"]) not in nets:
                dc_net = str(interface["network"])

.. dropdown:: Possible Solution for ``plugin.py``

    .. code-block:: python

        from firewheel.control.experiment_graph import AbstractPlugin, Vertex

        from vyos import VyOSConfigItem
        from vyos.helium118 import Helium118

        class Plugin(AbstractPlugin):
            """acme.firewall plugin documentation."""

            def run(self):
                """Add the firewall rules to prevent datacenter access."""
                for vert in self.g.get_vertices():
                    if vert.is_decorated_by(Helium118) and vert.name == "firewall.acme.com":
                        data_center_router = self.g.find_vertex("datacenter.acme.com")
                        nets = set()
                        for interface in vert.interfaces.interfaces:
                            nets.add(str(interface["network"]))

                        for interface in data_center_router.interfaces.interfaces:
                            if str(interface["network"]) not in nets:
                                dc_net = str(interface["network"])

                        rule = VyOSConfigItem("name", "drop_datacenter")
                        rule.add_children(VyOSConfigItem("default-action", "accept"))
                        rule.add_children(VyOSConfigItem("rule", "1"))
                        rule_1 = rule.find("rule")
                        dest = VyOSConfigItem("destination")
                        dest.add_children(VyOSConfigItem("address", f"{dc_net}"))
                        rule_1.add_children(dest)
                        rule_1.add_children(VyOSConfigItem("action", "drop"))

                        # Now we can use the set_firewall function to pass in a list of the new rule sets.
                        vert.assign_firewall_policies({"in": [rule]})

                        # Now it should be complete!



Testing our Solution
====================

Now that we have our second model component, we can go ahead and launch our experiment and test this solution.

**Questions to answer**:

* How do we launch the model?
* What tests need to occur to validate that our experiment is configured correctly?
* Was our model correct? If not, why?

.. dropdown:: Hint #1 (launching the model)

    If you made it this far and still need the hint for launching the model, please review the earlier tutorials.

    .. code-block:: bash

        firewheel experiment -r acme.topology acme.firewall minimega.launch

.. dropdown:: Hint #2 (what tests to run)

    As an Emulytics expert, not only do you have to know how to use Emulytics tools (like FIREWHEEL!) and deeply understand the system being modeled, but you also need to wear a Quality Assurance hat and understand how to test/validate the model.

    In our case, the objective was "Only *Building 2* residents can access the data center".
    Given the topology that we have, it seems reasonable to try the following tests:

    | **Test**: Can the Gateway (or anything beyond it) access the data center?
    | **Correct Response**: No

    | **Test**: Can *Building 1* residents access the data center?
    | **Correct Response**: No

    | **Test**: Can *Building 2* residents access the data center?
    | **Correct Response**: Yes

.. dropdown:: Hint #3 (how to test)

    Using miniweb, log into the ``gateway.acme.com`` VM and try to ping ``datacenter-0.acme.com``.
    miniweb *should* show the IP address for ``datacenter-0.acme.com``.

    Repeat with ``building1-host-0.acme.com`` and ``building2-host-0.acme.com``.

    .. dropdown:: Hint #3.1 (test results)

        | **Test**: Can the Gateway (or anything beyond it) access the data center?
        | **Acutal Response**: No!

        | **Test**: Can *Building 1* residents access the data center?
        | **Actual Response**: Yes???

        | **Test**: Can *Building 2* residents access the data center?
        | **Acutal Response**: Yes!

.. dropdown:: Hint #4 (debugging)

    Now that we know our model is wrong, we should review the assumptions we made.

    .. dropdown:: Hint #4.1 (assumptions)

        * We put the access control rules on the firewall. Is that the best place for them? Is it the only place?
        * Did we translate the real network diagram correctly into an emulated version? Are there parts that are ambiguous?

    .. dropdown:: Hint #4.2 (Root Cause)

        Fundamentally, we misunderstood basic networking fundamentals leading to this bug.
        Specifically, we assumed that when three routers are connected via a switch (i.e., are on the same collision domain), that the packet from ``building1.acme.com`` would be routed by ``firewall.acme.com`` to ``building2.acme.com``.
        However, when networking devices share a collision domain, the packet can simply be "switched" to ``build2.acme.com`` via the connecting Switch.
        In this case, the initial network diagram did not provide IP addresses and so we made an **assumption** that the buildings were on the same collision domain (rather than separate ones).
        This tutorial demonstrates that even small assumptions can have large implications on the model!

        What are our possible fixes?

    .. dropdown:: Hint #4.3 (fixing the problem)

        There are a couple ways to solve this issue. Which one to choose should entirely depend on the research question being answered! Here are two possibilities:

        1. Ensuring that the *Building 1* and *Building 2* routers are not on the same switch to force packets to traverse the firewall. Does adding this extra layer reduce (or increase) fidelity?
        2. Add additional firewall rules onto the ``building2.acme.com``. Additionally, we could remove them from the firewall. Each of these choices changes the experiment slightly and *may* impact experiment fidelity.

        We leave it up to the model developer (hopefully with input from model stakeholders) to choose a fix, implement it, and test it.


Model Refinement
================

Now that we have completed our objective, are there other modifications that could/should be made to the model?
We will not provide hints in this section, but here are a few questions to answer.

**Questions to answer**:

* Does the model help answer my research question?
* Do I need to extract data for post-experiment analysis?
* Is the model usable?
* Will other researchers understand what the model does (i.e., is it properly documented)?
