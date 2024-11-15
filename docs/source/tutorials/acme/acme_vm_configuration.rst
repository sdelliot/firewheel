*******************
Harden the Firewall
*******************

This module will use :ref:`vm_resource_system` to slightly modify the firewalls's configuration.
In this case, we will simply use the :py:meth:`run_executable <base_objects.VMEndpoint.run_executable>` method to execute a system-level command in our VM.

For the sake of this tutorial, let's pretend the system administrator of the ACME network wants to harden the firewall.
Therefore, they have decided to only allow access to the machine through the physical console and therefore the SSH server needs to be turned off.
Since the firewall is a :py:class:`VyOS Helium118 <vyos.helium118.Helium118>` router, the command to turn off SSH is simply ``service ssh stop``.
Configuring a VM to run a command like this only requires calling the :py:meth:`run_executable <base_objects.VMEndpoint.run_executable>` function on the firewall's object in the graph.

.. note::

    The technically better way to do this would be to modify the a router's configuration to ensure that the SSH server is disabled. However, we're using the ``service`` system command to make this tutorial more generally applicable.

Modifying the Topology
======================

The firewall was created in the ACME topology's ``build_front()`` function which should look like this:

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

We need to add the following :py:meth:`run_executable <base_objects.VMEndpoint.run_executable>` call to the ``fw`` object:

 .. code-block:: python

    firewall.run_executable(-50, "/usr/sbin/service", "ssh stop")

This will run the ``service`` command at schedule time ``-50``.
It is not strictly required that the absolute path to the program be specified, but it is far safer do so rather than making any assumptions about how the VM environment will resolve program names.
The modified ``build_front()`` function should now look like this (specifically, the addition of line 39):

.. code-block:: python
    :linenos:
    :emphasize-lines: 39

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
        firewall.run_executable(-50, "/usr/sbin/service", "ssh stop")

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

Once the topology is relaunched and all VMs are configured, use a VNC client in order to access the firewall VM:

.. code-block:: bash

    $ firewheel vm list name=firewall vnc hostname

Once you are in the VM, run the following command to verify that the SSH server is off:

.. code-block:: bash

    $ sudo service ssh status

A message should appear that the command "failed" since no PID file was found for SSH.
This indicates that SSH is no longer running (otherwise there would be an active PID file) which means our command was successful.
