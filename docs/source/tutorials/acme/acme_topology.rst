.. _acme-topology:

*********************************
Creating the ACME Topology Plugin
*********************************

Recall that the ACME network will look like:

.. image:: network_topology.png
   :alt: ACME Network Topology

The actual code that builds the topology is the ACME model component's plugin which we specified as ``plugin.py`` in the ``MANIFEST`` file.
Therefore, open the file ``acme/topology/plugin.py`` to get started.

.. _acme-topo-abstract_plugin:

Opening Our Plugin
==================

Within every plugin file, FIREWHEEL automatically looks for a plugin class to define the plugin's execution.
This class must meet two criteria.

First, the class that gets declared must inherit from :py:class:`AbstractPlugin <firewheel.control.experiment_graph.AbstractPlugin>`.
This guarantees that the :ref:`experiment-graph` instance is properly handled and located in the variable ``self.g``.
Additionally, this inheritance also provides a logger in ``self.log`` to each plugin to facilitate easy debugging.

Second, the plugin must have a ``run()`` method.
This is the method that gets invoked by FIREWHEEL to kick off the plugin.
The ``run()`` method can also take parameters, if needed, for the topology.

As a note, only one such plugin class may be defined per plugin file (more would be ambiguous and therefore will cause FIREWHEEL to raise an error).

With this context in mind, we will be editing the ``run()`` method first.

Open the file ``acme/topology/plugin.py`` to get started.

It should look something like this:

 .. code-block:: python

    from firewheel.control.experiment_graph import AbstractPlugin, Vertex

    class Plugin(AbstractPlugin):
        """acme.topology plugin documentation."""

        def run(self):
            """Run method documentation."""
            # TODO: Implement plugin actions here
            pass


.. _acme-topo-run:

Implementing the Plugin
=======================

Because this topology is more complex than a few VMs, we recommend splitting up the functionality into separate methods.
We can view the network graph as four distinct sections; the *Front*, *Building 1*, *Building 2*, and the *Data center*.
Therefore, we can build the sections in individual methods and tie them all together in ``run()``.

Set up
------
Before working on any particular part of the topology, we should first add a few necessary import statements.
Add the following to the top of ``plugin.py``.

.. code-block:: python

    from netaddr import IPNetwork

    from firewheel.control.experiment_graph import Vertex, AbstractPlugin

    from base_objects import Switch
    from vyos.helium118 import Helium118
    from linux.ubuntu2204 import Ubuntu2204Server, Ubuntu2204Desktop

These imports provide the necessary graph objects needed to create the topology.
Additionally, we will use :py:mod:`netaddr` to facilitate assigning IP addresses easier.

Let's initialize a few instance variables which can be used when creating the topology.
Using :py:mod:`netaddr`  we will create an external-facing network (e.g. "Internet" facing).
We aren't going to put anything external to the ACME enterprise in this tutorial, but you could add to this topology by providing external services.
The external network is going to be ``1.0.0.0/24``.

Next, we need an internal network for routing between the distinct sections of the enterprise.
We're going to use ``10.0.0.0/8`` and the subsequently break up the network into subnet blocks each with 255 IP addresses.

While users can define IP addresses with simple Python strings, for complex topologies we recommend using the :py:class:`netaddr.IPNetwork` and :py:class:`netaddr.IPAddress` classes to specify various network spaces.
:py:class:`netaddr.IPNetwork` provides a generator (:py:meth:`iter_hosts() <netaddr.IPNetwork.iter_hosts>`) that allows you to walk through the entire IP space.
The generator provides :py:class:`IPAddress <netaddr.IPAddress>` objects.
Therefore, we can use standard python syntax to get the next available :py:class:`IPAddress <netaddr.IPAddress>` (e.g. ``next(network_iter)``).
We will use this generator method throughout the creation of the ACME topology.

Here is our initial ``run()`` method.

.. code-block:: python

    def run(self):
        """Run method documentation."""
        # Create an external-facing network and an iterator for that network.
        # The iterator will provide the next available netaddr.IPAddress for the given
        # network.
        self.external_network = IPNetwork("1.0.0.0/24")
        external_network_iter = self.external_network.iter_hosts()

        # Create an internal facing network
        internal_networks = IPNetwork("10.0.0.0/8")

        # Break the internal network into various subnets
        # https://netaddr.readthedocs.io/en/latest/tutorial_01.html#supernets-and-subnets
        self.internal_subnets = internal_networks.subnet(24)

Building the Front
------------------
Now we are ready to build out the first part of the topology which we will call the "front".
The "front" of the enterprise consists of the gateway router and the firewall.
We will create a new method called ``build_front()``.
For this method, we can pass in the external IP network for the gateway.

.. code-block:: python

    def build_front(self, ext_ip):
        pass

Now we need to create the gateway router.
We create a vertex by instantiating a :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>` object and passing it the graph (``self.g``) as well as the name of the vertex.
The ``plugin.py`` template has already imported :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>` for you from :py:mod:`firewheel.control.experiment_graph`.
Once we have created a :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>`, we can decorate it as a specific object type.
In this case, we want the gateway to be a VyOS router using the Helium 1.1.8 release.
We have imported the the :py:class:`Helium118 <vyos.helium118.Helium118>` object already (from the :ref:`vyos.helium118_mc` MC) so we can use it to decorate our gateway.

.. note::
    Vertices can be given default image types in the case where a specific image class isn't known at topology creation.
    We could have decorated this :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>` with :py:class:`GenericRouter <generic_vm_objects.GenericRouter>` (from the :ref:`generic_vm_objects_mc` MC) and it would have subsequently been decorated as :py:class:`Helium118 <vyos.helium118.Helium118>` due to the defaults set in the :ref:`minimega.resolve_vm_images_mc` model component.
    See :ref:`minimega.resolve_vm_images_mc` for more details.


.. code-block:: python

    def build_front(self, ext_ip):
        # Build the gateway
        gateway = Vertex(self.g, "gateway.acme.com")
        gateway.decorate(Helium118)


In FIREWHEEL :py:class:`Switches <base_objects.Switch>` are essentially virtual network bridges which help connect two VMs.
Users *can* make a Switch into a VM if some specific switching technique is being evaluated, but typically, they will just be instantiated as an Open vSwitch bridge that is transparent to the VMs within the experiment.
A :py:class:`Switch <base_objects.Switch>` is created in a way that is very similar to the routers.
The only difference is that the :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>` is decorated with :py:class:`Switch <base_objects.Switch>`, which can be imported from :ref:`base_objects_mc`.

We can now create our "external" switch.

.. code-block:: python

    # Create the external switch
    ext_switch = Vertex(self.g, name="ACME-EXTERNAL")
    ext_switch.decorate(Switch)

Now that we have the :py:class:`Switch <base_objects.Switch>` and the gateway, we can connect them together.
We will use the IP address which was passed into the method.

.. code-block:: python

    # Connect the gateway to the external switch
    gateway.connect(
        ext_switch,  # The "Internet" facing Switch
        ext_ip,  # The external IP address for the gateway (e.g. 1.0.0.1)
        self.external_network.netmask  # The external subnet mask (e.g. 255.255.255.0)
    )


We then do the same thing to create the firewall and the switch to connect the firewall to the gateway.

.. code-block:: python

    # Build a switch to connect the gateway and firewall
    gateway_firewall_switch = Vertex(self.g, name="GW-FW")
    gateway_firewall_switch.decorate(Switch)

    # Build the firewall
    firewall = Vertex(self.g, "firewall.acme.com")
    firewall.decorate(Helium118)

We will want to create a network to generate the IP address for the gateway/firewall connection.
To do so, we can grab the next available subnet from our ``self.internal_subnets`` generator.

.. code-block:: python

    # Create a network and a generator for the network between
    # the gateway and firewall.
    gateway_firewall_network = next(self.internal_subnets)
    gateway_firewall_network_iter = gateway_firewall_network.iter_hosts()

Since this is a network local to the enterprise, let's have the routers use the `OSPF <https://en.wikipedia.org/wiki/Open_Shortest_Path_First>`__ routing protocol.
When using OSPF, you can call the :py:meth:`ospf_connect() <generic_vm_objects.GenericRouter.ospf_connect>` method on the router.
The :py:meth:`ospf_connect() <generic_vm_objects.GenericRouter.ospf_connect>` method requires that you specify the switch to connect the router to, the IP address for the router's interface, and the netmask of the IP.
This method takes care of all the relevant details to make sure that OSPF works on the newly created network interface.

.. code-block:: python

    # Connect the gateway and the firewall to their respective switches
    # We will use ``ospf_connect`` to ensure that the OSPF routes are propagated
    # correctly (as we want to use OSPF as routing protocol inside of the ACME network).
    gateway.ospf_connect(
        gateway_firewall_switch,
        next(gateway_firewall_network_iter),
        gateway_firewall_network.netmask,
    )
    firewall.ospf_connect(
        gateway_firewall_switch,
        next(gateway_firewall_network_iter),
        gateway_firewall_network.netmask,
    )

Finally, we return the firewall :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>` so that other parts of the topology can connect to them as well.

.. code-block:: python

    return firewall

The full ``build_front()`` method is:

.. code-block:: python

    def build_front(self, ext_ip):
        """Build the ACME infrastructure that is Internet-facing.

        This method will create the following topology::

                switch -- gateway -- switch -- firewall
            (ACME-EXTERNAL)         (GW-FW)

        Args:
            ext_ip (netaddr.IPAddress): The external IP address for the gateway
                (e.g. its Internet facing IP address).

        Returns:
            vyos.Helium118: The Firewall object.
        """

        # Build the gateway
        gateway = Vertex(self.g, "gateway.acme.com")
        gateway.decorate(Helium118)

        # Create the external switch
        ext_switch = Vertex(self.g, name="ACME-EXTERNAL")
        ext_switch.decorate(Switch)

        # Connect the gateway to the external switch
        gateway.connect(
            ext_switch,  # The "Internet" facing Switch
            ext_ip,  # The external IP address for the gateway (e.g. 1.0.0.1)
            self.external_network.netmask  # The external subnet mask (e.g. 255.255.255.0)
        )

        # Build a switch to connect the gateway and firewall
        gateway_firewall_switch = Vertex(self.g, name="GW-FW")
        gateway_firewall_switch.decorate(Switch)

        # Build the firewall
        firewall = Vertex(self.g, "firewall.acme.com")
        firewall.decorate(Helium118)

        # Create a network and a generator for the network between
        # the gateway and firewall.
        gateway_firewall_network = next(self.internal_subnets)
        gateway_firewall_network_iter = gateway_firewall_network.iter_hosts()

        # Connect the gateway and the firewall to their respective switches
        # We will use ``ospf_connect`` to ensure that the OSPF routes are propagated
        # correctly (as we want to use OSPF as routing protocol inside of the ACME network).
        gateway.ospf_connect(
            gateway_firewall_switch,
            next(gateway_firewall_network_iter),
            gateway_firewall_network.netmask,
        )
        firewall.ospf_connect(
            gateway_firewall_switch,
            next(gateway_firewall_network_iter),
            gateway_firewall_network.netmask,
        )
        return firewall


Updating ``run()``
------------------
Now that we have a method which will create the first part of our ACME network, we can update our ``run()`` method to call ``build_front()``.
Recall that we needed to pass in the an external IP address.

.. code-block:: python

    def run(self):
        ...
        # Create the gateway and firewall
        firewall = self.build_front(next(external_network_iter))

Now, we can create a new :py:class:`Switch <base_objects.Switch>` and a new subnet which will be used to connect both buildings to the firewall.

.. code-block:: python
    :emphasize-lines: 6-13

    def run(self):
        ...
        # Create the gateway and firewall
        firewall = self.build_front(next(external_network_iter))

        # Create an internal switch
        internal_switch = Vertex(self.g, name="ACME-INTERNAL")
        internal_switch.decorate(Switch)

        # Grab a subnet to use for connections to the internal switch
        internal_switch_network = next(self.internal_subnets)
        # Create a generator for the network
        internal_switch_network_iter = internal_switch_network.iter_hosts()

Once we have set up internal network and Switch, we can connect the firewall to that switch.

.. code-block:: python
    :emphasize-lines: 6-11

    def run(self):
        ...
        # Create a generator for the network
        internal_switch_network_iter = internal_switch_network.iter_hosts()

        # Connect the firewall to the internal switch
        firewall.ospf_connect(
            gateway_firewall_switch,
            next(gateway_firewall_network_iter),
            gateway_firewall_network.netmask,
        )

We are now ready to create a method to create a building.

Implementing ``build_building()``
---------------------------------

With the front done, it's now time to create an ACME building.
Since we want multiple buildings and the buildings themselves are very similar, we can make a single ``build_building()`` method that gets called multiple times from ``run()``.
We will want to pass in several method parameters to ``build_building()``:

* ``name`` - The name of the building (e.g. ``"building1"``).
* ``network`` - The :py:class:`netaddr.IPNetwork` subnet for the particular building. This will be used to connect all hosts within the building.
* ``num_hosts`` - The number of hosts the building should have.

.. code-block:: python

    def build_building(self, name, network, num_hosts=1):
        pass

Every building needs a router in order to connect to the rest of the ACME enterprise.
We use the ``name`` that was provided to the function as the name for the router.
Like the routers that were created in ``build_front()``, we decorate the :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>` as a :py:class:`Helium118 <vyos.helium118.Helium118>` router.

.. code-block:: python

    def build_building(self, name, network, num_hosts=1):
        """Create the building router and hosts.

        This is a single router with all of the hosts.
        Assuming that the building is called "building1" the topology will look like::

                switch ---- building1 ----- switch ------ hosts
            (ACME-INTERNAL)           (building1-switch)

        Args:
            name (str): The name of the building.
            network (netaddr.IPNetwork): The subnet for the building.
            num_hosts (int): The number of hosts the building should have.

        Returns:
            vyos.Helium118: The building router.
        """

        # Create the VyOS router which will connect the building to the ACME network.
        building = Vertex(self.g, name=f"{name}.acme.com")
        building.decorate(Helium118)

Now, we can create a new :py:class:`Switch <base_objects.Switch>` and a new :py:class:`IPAddress <netaddr.IPAddress>` generator which will be used to connect the building router to all building hosts.

.. code-block:: python

        # Create the building-specific switch
        building_sw = Vertex(self.g, name=f"{name}-switch")
        building_sw.decorate(Switch)

        # Create a generator for the building's network
        building_network_iter = network.iter_hosts()


We can now connect the building router to the building :py:class:`Switch <base_objects.Switch>`.
In this case, because none of the hosts use OSPF to communicate, we can directly connect the router to the switch using the :py:meth:`connect() <base_objects.VMEndpoint.connect>` (rather than using :py:meth:`ospf_connect() <generic_vm_objects.GenericRouter.ospf_connect>`).
However, because the ACME internal network uses OSPF to communicate, we will want to ensure that the building can be discovered by the rest of the ACME network.
Therefore, we use the :py:meth:`redistribute_ospf_connected() <generic_vm_objects.GenericRouter.redistribute_ospf_connected>` method to redistribute (i.e., advertise) networks that it is directly connected to (i.e., the building's network).
This will make the hosts routable (and discoverable) throughout the rest of the ACME enterprise.

.. code-block:: python

    # Create the building-specific switch
    building_sw = Vertex(self.g, name=f"{name}-switch")
    building_sw.decorate(Switch)

    # Create a generator for the building's network
    building_network_iter = network.iter_hosts()

    # Connect the building to the building Switch
    building.connect(building_sw, next(building_network_iter), network.netmask)

    # This redistributes routes for directly connected subnets to OSPF peers.
    # That is, enables these peers to be discoverable by the rest of the OSPF
    # routing infrastructure.
    building.redistribute_ospf_connected()


The building has a parameter which defines the number of end hosts that require access to the enterprise network (i.e. ``num_hosts``).
We can use a loop to create the requisite number of hosts.
In this case, we want to decorate our vertices with :py:class:`Ubuntu2204Desktop <linux.ubuntu2204.Ubuntu2204Desktop>`, which we imported from the :ref:`linux.ubuntu2204_mc`.
Once each host is created, we can add it to the building :py:class:`Switch <base_objects.Switch>`.

.. code-block:: python

        # Create the correct number of hosts
        for i in range(num_hosts):
            # Create a new host which is a Ubuntu Desktop
            host = Vertex(
                self.g,
                name=f"{name}-host-{i}.acme.com",  # e.g. "building1-host-1.acme.com"
            )
            host.decorate(Ubuntu2204Desktop)

            # Connect the host to the building's switch
            host.connect(
                building_sw,  # The building switch
                next(building_network_iter),  # The next available building IP address
                network.netmask,  # The building's subnet mask
            )

Now that all the hosts are connected we can return the building router to connect it to the ``ACME-INTERNAL`` :py:class:`Switch <base_objects.Switch>`.

.. code-block:: python

        return building

The full ``build_front()`` method is:

.. code-block:: python

    def build_building(self, name, network, num_hosts=1):
        """Create the building router and hosts.

        This is a single router with all of the hosts.
        Assuming that the building is called "building1" the topology will look like::

                switch ---- building1 ----- switch ------ hosts
            (ACME-INTERNAL)           (building1-switch)

        Args:
            name (str): The name of the building.
            network (netaddr.IPNetwork): The subnet for the building.
            num_hosts (int): The number of hosts the building should have.

        Returns:
            vyos.Helium118: The building router.
        """

        # Create the VyOS router which will connect the building to the ACME network.
        building = Vertex(self.g, name=f"{name}.acme.com")
        building.decorate(Helium118)

        # Create the building-specific switch
        building_sw = Vertex(self.g, name=f"{name}-switch")
        building_sw.decorate(Switch)

        # Create a generator for the building's network
        building_network_iter = network.iter_hosts()

        # Connect the building to the building Switch
        building.connect(building_sw, next(building_network_iter), network.netmask)

        # This redistribute routes for directly connected subnets to OSPF peers.
        # That is, enables these peers to be discoverable by the rest of the OSPF
        # routing infrastructure.
        building.redistribute_ospf_connected()

        # Create the correct number of hosts
        for i in range(num_hosts):
            # Create a new host which is a Ubuntu Desktop
            host = Vertex(
                self.g,
                name=f"{name}-host-{i}.acme.com",  # e.g. "building1-host-1.acme.com"
            )
            host.decorate(Ubuntu2204Desktop)

            # Connect the host to the building's switch
            host.connect(
                building_sw,  # The building switch
                next(building_network_iter),  # The next available building IP address
                network.netmask,  # The building's subnet mask
            )

        return building

Adding buildings to ``run()``
-----------------------------
Recall that we had just connected the firewall to the internal switch in the ``run()`` method.

.. code-block:: python

    def run(self):
        ...
        # Connect the Firewall to the internal switch
        firewall.ospf_connect(
            internal_switch,
            next(internal_switch_network_iter),
            internal_switch_network.netmask,
        )

We already have all the pieces in place to create our two buildings and connect them to the same internal switch.

.. code-block:: python

    def run(self):
        ...
       building_1 = self.build_building(
            "building1",  # The name of the building
            next(self.internal_subnets),  # The building network
            num_hosts=3,  # The number of hosts for the building
        )

        # Connect the first building router to the internal switch.
        building_1.ospf_connect(
            internal_switch,
            next(internal_switch_network_iter),
            internal_switch_network.netmask,
        )

        # Create our second building
        building_2 = self.build_building(
            "building2",  # The name of the building
            next(self.internal_subnets),  # The building network
            num_hosts=3,  # The number of hosts for the building
        )

        # Connect the second building router to the internal switch.
        building_2.ospf_connect(
            internal_switch,
            next(internal_switch_network_iter),
            internal_switch_network.netmask,
        )


Now that our buildings are ready, we can begin constructing the data center.
This will also be a separate method.

Implementing ``build_datacenter()``
-----------------------------------

The data center hosts the servers for our fictional ACME enterprise.
The slight difference for this method is that the data center is housed in Building 2 and therefore uses the Building 2 router to connect into the rest of the internal network.
This is set by passing in the Building 2 router as the first parameter of the ``build_datacenter()`` method.
Additionally, the data center will need two different networks, one for connecting the DC to the building and a second for connecting the DC to its various servers.

.. code-block:: python

    def build_datacenter(self, building, uplink_network, dc_network):
        pass

The ``build_datacenter()`` method will look similar to creating a building.
We will create a DC :py:class:`Vertex <firewheel.control.experiment_graph.Vertex>` and decorate it as a a :py:class:`Helium118 <vyos.helium118.Helium118>` router.
We will then create a :py:class:`Switch <base_objects.Switch>` and an :py:class:`IPAddress <netaddr.IPAddress>` generator from the ``uplink_network`` and connect the DC router and the building router to the switch using the :py:meth:`ospf_connect() <generic_vm_objects.GenericRouter.ospf_connect>` method.
Next, we will create the internal DC switch and a :py:func:`for loop <for>` to create all of our servers.
In this case, the servers will be decorated as a :py:class:`Ubuntu2204Server <linux.ubuntu2204.Ubuntu2204Server>` (rather than a :py:class:`Ubuntu2204Desktop <linux.ubuntu2204.Ubuntu2204Desktop>`).

The full method looks like:

.. code-block:: python

    def build_datacenter(self, building, uplink_network, dc_network):
        """Create the data center.

        This is a single router with all of the servers::

           building2 ------ switch ------ datacenter ------ switch ------ servers
                     (building2-DC-switch)                (DC-switch)

        Args:
            building (vyos.Helium118): The Building router which contains the data center.
            uplink_network (netaddr.IPNetwork): The network to connect the DC to the building.
            dc_network (netaddr.IPNetwork): The network for the data center.
        """
        # Create a switch to connect the DC with the building
        building_dc_sw = Vertex(self.g, name=f"{building.name}-DC-switch")
        building_dc_sw.decorate(Switch)

        # Create the datacenter router
        datacenter = Vertex(self.g, name="datacenter.acme.com")
        datacenter.decorate(Helium118)

        # Create a generator for the building's network
        uplink_network_iter = uplink_network.iter_hosts()

        # Connect the building to the building-DC-switch
        building.ospf_connect(
            building_dc_sw, next(uplink_network_iter), uplink_network.netmask
        )

        # Connect the datacenter to the building-DC-switch
        datacenter.ospf_connect(
            building_dc_sw, next(uplink_network_iter), uplink_network.netmask
        )

        # Make the datacenter internal switch and connect
        datacenter_sw = Vertex(self.g, name="DC-switch")
        datacenter_sw.decorate(Switch)

        # Create a generator for the DC's network
        dc_network_iter = dc_network.iter_hosts()

        # Connect the DC to the internal switch
        datacenter.connect(datacenter_sw, next(dc_network_iter), dc_network.netmask)

        # This redistribute routes for directly connected subnets to OSPF peers.
        # That is, enables these peers to be discoverable by the rest of the OSPF
        # routing infrastructure.
        datacenter.redistribute_ospf_connected()

        # Make servers
        for i in range(3):
            # Create a new Ubuntu server and add connect it to the DC network switch
            server = Vertex(self.g, name=f"datacenter-{i}.acme.com")
            server.decorate(Ubuntu2204Server)
            server.connect(datacenter_sw, next(dc_network_iter), dc_network.netmask)


Calling ``build_datacenter()``
------------------------------

Lastly, we need to call the ``build_datacenter()`` from our run function.
You can simply add the following lines to the bottom of ``run()``.

.. code-block:: python

        # Build our data center
        self.build_datacenter(
            building_2,  # The building Vertex
            next(
                self.internal_subnets
            ),  # Add a network to connect the DC to the building
            next(self.internal_subnets),  # Add a network which is internal to the DC
        )

Here is what the full ``run()`` function should look like:

 .. code-block:: python

    def run(self):
        """Run method documentation."""
        # Create an external-facing network and an iterator for that network.
        # The iterator will provide the next available netaddr.IPAddress for the given
        # network.
        self.external_network = IPNetwork("1.0.0.0/24")
        external_network_iter = self.external_network.iter_hosts()

        # Create an internal facing network
        internal_networks = IPNetwork("10.0.0.0/8")

        # Break the internal network into various subnets
        # https://netaddr.readthedocs.io/en/latest/tutorial_01.html#supernets-and-subnets
        self.internal_subnets = internal_networks.subnet(24)

        # Create the gateway and firewall
        firewall = self.build_front(next(external_network_iter))

        # Create an internal switch
        internal_switch = Vertex(self.g, name="ACME-INTERNAL")
        internal_switch.decorate(Switch)

        # Grab a subnet to use for connections to the internal switch
        internal_switch_network = next(self.internal_subnets)
        # Create a generator for the network
        internal_switch_network_iter = internal_switch_network.iter_hosts()

        # Connect the Firewall to the internal switch
        firewall.ospf_connect(
            internal_switch,
            next(internal_switch_network_iter),
            internal_switch_network.netmask,
        )

        # Create our first building
        building_1 = self.build_building(
            "building1",  # The name of the building
            next(self.internal_subnets),  # The building network
            num_hosts=3,  # The number of hosts for the building
        )

        # Connect the first building router to the internal switch.
        building_1.ospf_connect(
            internal_switch,
            next(internal_switch_network_iter),
            internal_switch_network.netmask,
        )

        # Create our second building
        building_2 = self.build_building(
            "building2",  # The name of the building
            next(self.internal_subnets),  # The building network
            num_hosts=3,  # The number of hosts for the building
        )

        # Connect the second building router to the internal switch.
        building_2.ospf_connect(
            internal_switch,
            next(internal_switch_network_iter),
            internal_switch_network.netmask,
        )

        # Build our data center
        self.build_datacenter(
            building_2,  # The building Vertex
            next(
                self.internal_subnets
            ),  # Add a network to connect the DC to the building
            next(self.internal_subnets),  # Add a network which is internal to the DC
        )



Putting it All Together
-----------------------

At this point, you can save your file and close the editor.
It is now time to verify that your topology works as expected.

For reference, the full ``plugin.py`` file should look something like this:

.. code-block:: python

    from netaddr import IPNetwork

    from firewheel.control.experiment_graph import Vertex, AbstractPlugin

    from base_objects import Switch
    from vyos.helium118 import Helium118
    from linux.ubuntu2204 import Ubuntu2204Server, Ubuntu2204Desktop


    class Plugin(AbstractPlugin):
        """acme.topology plugin documentation."""

        def run(self):
            """Run method documentation."""
            # Create an external-facing network and an iterator for that network.
            # The iterator will provide the next available netaddr.IPAddress for the given
            # network.
            self.external_network = IPNetwork("1.0.0.0/24")
            external_network_iter = self.external_network.iter_hosts()

            # Create an internal facing network
            internal_networks = IPNetwork("10.0.0.0/8")

            # Break the internal network into various subnets
            # https://netaddr.readthedocs.io/en/latest/tutorial_01.html#supernets-and-subnets
            self.internal_subnets = internal_networks.subnet(24)

            # Create the gateway and firewall
            firewall = self.build_front(next(external_network_iter))

            # Create an internal switch
            internal_switch = Vertex(self.g, name="ACME-INTERNAL")
            internal_switch.decorate(Switch)

            # Grab a subnet to use for connections to the internal switch
            internal_switch_network = next(self.internal_subnets)
            # Create a generator for the network
            internal_switch_network_iter = internal_switch_network.iter_hosts()

            # Connect the Firewall to the internal switch
            firewall.ospf_connect(
                internal_switch,
                next(internal_switch_network_iter),
                internal_switch_network.netmask,
            )

            # Create our first building
            building_1 = self.build_building(
                "building1",  # The name of the building
                next(self.internal_subnets),  # The building network
                num_hosts=3,  # The number of hosts for the building
            )

            # Connect the first building router to the internal switch.
            building_1.ospf_connect(
                internal_switch,
                next(internal_switch_network_iter),
                internal_switch_network.netmask,
            )

            # Create our second building
            building_2 = self.build_building(
                "building2",  # The name of the building
                next(self.internal_subnets),  # The building network
                num_hosts=3,  # The number of hosts for the building
            )

            # Connect the second building router to the internal switch.
            building_2.ospf_connect(
                internal_switch,
                next(internal_switch_network_iter),
                internal_switch_network.netmask,
            )

            # Build our data center
            self.build_datacenter(
                building_2,  # The building Vertex
                next(
                    self.internal_subnets
                ),  # Add a network to connect the DC to the building
                next(self.internal_subnets),  # Add a network which is internal to the DC
            )

        def build_front(self, ext_ip):
            """Build the ACME infrastructure that is Internet-facing.

            This method will create the following topology::

                    switch -- gateway -- switch -- firewall
                (ACME-EXTERNAL)         (GW-FW)

            Args:
                ext_ip (netaddr.IPAddress): The external IP address for the gateway
                    (e.g. its Internet facing IP address).

            Returns:
                vyos.Helium118: The Firewall object.
            """

            # Build the gateway
            gateway = Vertex(self.g, "gateway.acme.com")
            gateway.decorate(Helium118)

            # Create the external switch
            ext_switch = Vertex(self.g, name="ACME-EXTERNAL")
            ext_switch.decorate(Switch)

            # Connect the gateway to the external switch
            gateway.connect(
                ext_switch,  # The "Internet" facing Switch
                ext_ip,  # The external IP address for the gateway (e.g. 1.0.0.1)
                self.external_network.netmask,  # The external subnet mask (e.g. 255.255.255.0)
            )

            # Build a switch to connect the gateway and firewall
            gateway_firewall_switch = Vertex(self.g, name="GW-FW")
            gateway_firewall_switch.decorate(Switch)

            # Build the firewall
            firewall = Vertex(self.g, "firewall.acme.com")
            firewall.decorate(Helium118)

            # Create a network and a generator for the network between
            # the gateway and firewall.
            gateway_firewall_network = next(self.internal_subnets)
            gateway_firewall_network_iter = gateway_firewall_network.iter_hosts()

            # Connect the gateway and the firewall to their respective switches
            # We will use ``ospf_connect`` to ensure that the OSPF routes are propagated
            # correctly (as we want to use OSPF as routing protocol inside of the ACME network).
            gateway.ospf_connect(
                gateway_firewall_switch,
                next(gateway_firewall_network_iter),
                gateway_firewall_network.netmask,
            )
            firewall.ospf_connect(
                gateway_firewall_switch,
                next(gateway_firewall_network_iter),
                gateway_firewall_network.netmask,
            )
            return firewall

        def build_building(self, name, network, num_hosts=1):
            """Create the building router and hosts.

            This is a single router with all of the hosts.
            Assuming that the building is called "building1" the topology will look like::

                    switch ---- building1 ----- switch ------ hosts
                (ACME-INTERNAL)           (building1-switch)

            Args:
                name (str): The name of the building.
                network (netaddr.IPNetwork): The subnet for the building.
                num_hosts (int): The number of hosts the building should have.

            Returns:
                vyos.Helium118: The building router.
            """

            # Create the VyOS router which will connect the building to the ACME network.
            building = Vertex(self.g, name=f"{name}.acme.com")
            building.decorate(Helium118)

            # Create the building-specific switch
            building_sw = Vertex(self.g, name=f"{name}-switch")
            building_sw.decorate(Switch)

            # Create a generator for the building's network
            building_network_iter = network.iter_hosts()

            # Connect the building to the building Switch
            building.connect(building_sw, next(building_network_iter), network.netmask)

            # This redistribute routes for directly connected subnets to OSPF peers.
            # That is, enables these peers to be discoverable by the rest of the OSPF
            # routing infrastructure.
            building.redistribute_ospf_connected()

            # Create the correct number of hosts
            for i in range(num_hosts):
                # Create a new host which is a Ubuntu Desktop
                host = Vertex(
                    self.g,
                    name=f"{name}-host-{i}.acme.com",  # e.g. "building1-host-1.acme.com"
                )
                host.decorate(Ubuntu2204Desktop)

                # Connect the host to the building's switch
                host.connect(
                    building_sw,  # The building switch
                    next(building_network_iter),  # The next available building IP address
                    network.netmask,  # The building's subnet mask
                )

            return building

        def build_datacenter(self, building, uplink_network, dc_network):
            """Create the data center.

            This is a single router with all of the servers::

            building2 ------ switch ------ datacenter ------ switch ------ servers
                        (building2-DC-switch)                (DC-switch)

            Args:
                building (vyos.Helium118): The Building router which contains the data center.
                uplink_network (netaddr.IPNetwork): The network to connect the DC to the building.
                dc_network (netaddr.IPNetwork): The network for the data center.
            """
            # Create a switch to connect the DC with the building
            building_dc_sw = Vertex(self.g, name=f"{building.name}-DC-switch")
            building_dc_sw.decorate(Switch)

            # Create the datacenter router
            datacenter = Vertex(self.g, name="datacenter.acme.com")
            datacenter.decorate(Helium118)

            # Create a generator for the building's network
            uplink_network_iter = uplink_network.iter_hosts()

            # Connect the building to the building-DC-switch
            building.ospf_connect(
                building_dc_sw, next(uplink_network_iter), uplink_network.netmask
            )

            # Connect the datacenter to the building-DC-switch
            datacenter.ospf_connect(
                building_dc_sw, next(uplink_network_iter), uplink_network.netmask
            )

            # Make the datacenter internal switch and connect
            datacenter_sw = Vertex(self.g, name="DC-switch")
            datacenter_sw.decorate(Switch)

            # Create a generator for the DC's network
            dc_network_iter = dc_network.iter_hosts()

            # Connect the DC to the internal switch
            datacenter.connect(datacenter_sw, next(dc_network_iter), dc_network.netmask)

            # This redistribute routes for directly connected subnets to OSPF peers.
            # That is, enables these peers to be discoverable by the rest of the OSPF
            # routing infrastructure.
            datacenter.redistribute_ospf_connected()

            # Make servers
            for i in range(3):
                # Create a new Ubuntu server and add connect it to the DC network switch
                server = Vertex(self.g, name=f"datacenter-{i}.acme.com")
                server.decorate(Ubuntu2204Server)
                server.connect(datacenter_sw, next(dc_network_iter), dc_network.netmask)
