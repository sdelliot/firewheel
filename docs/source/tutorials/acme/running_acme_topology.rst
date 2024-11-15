.. _running-acme-topo:

*************************
Testing the ACME Topology
*************************

Now that we have created our ``acme.topology`` MC, we can test it to see it if works as expected.
First, we can try executing it without launching any VMs.
This helps us find any syntax errors or issues with the ``MANIFEST`` file.

To do so, we can run::

    $ firewheel experiment acme.topology

You should see the following output:


.. code-block:: bash

    $ firewheel experiment acme.topology

    Do you want to execute /tmp/acme/topology/INSTALL [y/n/v/vc/q]: y
    Starting to install acme.topology!
    The acme.topology INSTALL file currently doesn't do anything!
    Installed acme.topology!
    Adding vyos-1.1.8.qc2.xz to cache. This may take a while. \ 0:00:12


                Model Components Executed
    ┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
    ┃ Model Component Name ┃   Result   ┃     Timing     ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
    │ misc.blank_graph     │         OK │  0.001 seconds │
    │ base_objects         │         OK │  0.010 seconds │
    │ generic_vm_objects   │         OK │  0.002 seconds │
    │ linux.base_objects   │         OK │  0.020 seconds │
    │ linux.ubuntu         │         OK │  0.018 seconds │
    │ linux.ubuntu2204     │         OK │  0.028 seconds │
    │ vyos                 │         OK │  0.030 seconds │
    │ vyos.helium118       │         OK │ 12.123 seconds │
    │ acme.topology        │         OK │  0.010 seconds │
    ├──────────────────────┼────────────┼────────────────┤
    │                      │ Total Time │ 16.283 seconds │
    └──────────────────────┴────────────┴────────────────┘
        Dependency resolution took 0.812 seconds

.. note::
    We can answer ``y`` to the question ``"Do you want to execute /tmp/acme/topology/INSTALL"`` as this file does not perform any meaningful actions and then we will not be asked to install the MC again.

.. note::
    If this is the first time you are running an experiment, you may see output which indicates that various image files are being cached: e.g. ``Adding vyos-1.1.8.qc2.xz to cache. This may take a while.``. The images are being cached for quicker access in future experiments.

If any errors are found, fix them before moving on to the next step.

Launching the Topology
======================
Now we are ready to launch the topology.
We can instantiate it with `minimega <https://www.sandia.gov/minimega/>`__ by using the :ref:`minimega.launch_mc` MC::

    $ firewheel experiment acme.topology minimega.launch

You should see the following output:

.. code-block:: bash

    $ firewheel experiment acme.topology minimega.launch


                        Model Components Executed
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
    ┃      Model Component Name       ┃   Result   ┃     Timing      ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
    │ misc.blank_graph                │         OK │   0.001 seconds │
    │ base_objects                    │         OK │   0.011 seconds │
    │ linux.base_objects              │         OK │   0.022 seconds │
    │ generic_vm_objects              │         OK │   0.001 seconds │
    │ vyos                            │         OK │   0.018 seconds │
    │ vyos.helium118                  │         OK │   0.016 seconds │
    │ linux.ubuntu                    │         OK │   0.020 seconds │
    │ linux.ubuntu2204                │         OK │   0.045 seconds │
    │ acme.topology                   │         OK │   0.011 seconds │
    │ minimega.emulated_entities      │         OK │   0.007 seconds │
    │ minimega.testbed_available      │         OK │   0.026 seconds │
    │ linux.ubuntu1604                │         OK │ 103.180 seconds │
    │ minimega.create_mac_addresses   │         OK │   0.004 seconds │
    │ minimega.resolve_vm_images      │         OK │   0.025 seconds │
    │ minimega.configure_ips          │         OK │   0.002 seconds │
    │ minimega.send_miniweb_arp       │         OK │   0.001 seconds │
    │ minimega.schedules_ready        │         OK │   0.000 seconds │
    │ vm_resource.schedule            │         OK │   0.054 seconds │
    │ vm_resource.validate            │         OK │   0.015 seconds │
    │ minimega.parse_experiment_graph │         OK │   5.089 seconds │
    │ minimega.launch                 │         OK │   0.000 seconds │
    ├─────────────────────────────────┼────────────┼─────────────────┤
    │                                 │ Total Time │ 111.348 seconds │
    └─────────────────────────────────┴────────────┴─────────────────┘
                Dependency resolution took 2.556 seconds


Once the topology is up and running you can use the :ref:`helper_vm_mix` command to check the state of the environment:

.. code-block:: bash

    $ firewheel vm mix
                                        VM Mix
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
    ┃ VM Image                         ┃ Power State ┃ VM Resource State ┃ Count ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
    │ ubuntu-22.04-server-amd64.qcow2  │ RUNNING     │ configured        │ 3     │
    ├──────────────────────────────────┼─────────────┼───────────────────┼───────┤
    │ vyos-1.1.8.qc2                   │ RUNNING     │ configured        │ 5     │
    ├──────────────────────────────────┼─────────────┼───────────────────┼───────┤
    │ ubuntu-22.04-desktop-amd64.qcow2 │ RUNNING     │ configuring       │ 6     │
    ├──────────────────────────────────┼─────────────┼───────────────────┼───────┤
    │                                  │             │ Total Scheduled   │ 14    │
    └──────────────────────────────────┴─────────────┴───────────────────┴───────┘


Checking Connectivity
=====================
Once all of the nodes have been ``configured`` we can verify that the graph is connected as expected.
For this tutorial, we will use `miniweb <https://www.sandia.gov/minimega/module-10-web-interface-and-connecting-to-a-virtual-machine-with-vnc/>`__ to connect to the VMs.
Please see :ref:`router-tree-miniweb` for details on connecting to miniweb.

Once you are connected to miniweb, you can log into several of the VMs and verify connectivity manually via ping.

.. note ::
    We recommend that your VMs initially use simple default user names/passwords for ease of use.
    For example, VMs that are Ubuntu-based might have a default username of ``ubuntu`` and a default password of ``ubuntu``, while VMs that are VyOS-based might have a default username of ``vyos`` and a default password of ``vyos``.
    Once users are familiar with FIREWHEEL, you might choose alternate passwords for your VMs for more security.


For our experiment we at least want to verify that a VM located in *Building 1* can access the *data center* servers prior to installation of the new access control rules.
In miniweb, you can search for ``building1-host-0.acme.com`` and then click the ``connect`` button to join the VNC session.

.. dropdown:: *Hint*

   1. Find the IP address of one of the data center servers. (i.e., log into a server and run ``ifconfig``.)
   2. Now, log into ``building1-host-0.acme.com``
   3. Attempt to ping the data center IP address from our *Building 1* host.
   4. If the ping is successful, the topology has launched correctly
