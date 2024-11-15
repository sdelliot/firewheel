.. _simple-server-tutorial:

#######################
Simple Server Tutorials
#######################

This tutorial walks through creating a relatively simple experiment in which users start a simple web server, access a web page, and analyze the resulting data.
The topology will start off with only two VMs (a client and a server), but will grow more complex.

At a high-level the topology will look like:

.. image:: simple_server/images/simple_server_topology.png
   :alt: High-level topology

To make this tutorial simple, we will be using Python's built in web server to host a single automatically generated file.
The client will pull the file using `curl <https://curl.se>`__ and will measure the speed of the download.

.. note::
   The completed Model Component can be found at :ref:`tutorials.simple_server_mc`.

.. _simple-server-getting-started:

***************
Getting Started
***************

Before creating any Model Components, we recommend that users think through the creation of this topology to understand how to translate the high-level objective into an experiment.

.. note::
    Model Components (MCs) are the building blocks of a FIREWHEEL experiment.
    Essentially they are folders, which may contain code, VM images, and/or other resources.
    Running a FIREWHEEL experiment is done by telling FIREWHEEL which Model Components define the network topology and any actions to be taken, and how the experiment should be "launched".
    A Model Component’s folder must contain a ``MANIFEST`` file that identifies it to FIREWHEEL as a Model Component, by declaring its name, contents, dependencies, and what properties it provides to other MCs.
    For more information about Model Components, see :ref:`model_components`.

Some questions to answer before starting include:

#. How many Model Components will I need/want?
#. Will my MCs have any dependencies?
#. What assumptions am I making about this experiment?
#. How will I validate my results?

How many Model Components will I need/want?
===========================================

Model Components should each accomplish one specific goal.
They should also be readable by others.
Lastly, they should be as reusable as possible.
That is, you should minimize future duplication of code.
Our objective is to measure the speed at which the web server returns a given file.
Given this exact tutorial, we will accomplish this goal with a single Model Component.
However, be mindful of the reusability of your Model Components.
If we used a more complex web server (e.g. Apache or NGINX) it would be wise to create multiple agnostic Model Components.
That way, future experiments could use the web server Model Component without any of the experiment specific information.

Will my MC have any dependencies?
=================================

To build this topology, we will first need a Model Component that provides the :ref:`experiment-graph` attribute (e.g. ``graph``).
Once a graph is available to use, we will need to add vertices to that graph and then specify what kind of vertices they are.
We can assume that both the server and client both run Ubuntu Server 16.04.
Additionally, a single switch will connect them.
Therefore, two types of vertices will be used: :py:class:`Ubuntu1604Server <linux.ubuntu1604.Ubuntu1604Server>` and :py:class:`Switch <base_objects.Switch>`.
In order to be able to import those classes within the topology file we need to depend on the modules that provide them.
In this case, the :ref:`base_objects_mc` and the :ref:`linux.ubuntu1604_mc` Model Components.
If you look at these Model Components you'll see the definitions for various Model Component objects which can be imported and used to help build out the experiment.


What assumptions am I making about this experiment?
===================================================

While it is almost impossible to identify *all* assumptions, it is always important to identify assumptions which might impact the validity of the experiment.
For this tutorial, the biggest assumption being made is that the OS types/versions are representative of environment being modeled.
One must be careful as this may not always be the case and will generate unexpected behavior.
When things go awry, keeping one's assumptions in mind makes debugging easier.

**How will I validate my results?**

For this tutorial, we will be using Python to analyze the speed of the download.

*************************************
Part 1: Building the Initial Topology
*************************************

.. toctree::
   :maxdepth: 2

   simple_server/simple_server_manifest.rst
   simple_server/simple_server_topology.rst
   simple_server/testing_connectivity.rst

***************************
Part 2: Adding VM Resources
***************************

.. toctree::
   :maxdepth: 2

   simple_server/vm_configuration.rst
   simple_server/vmr_debugging.rst
   simple_server/manual_interaction.rst

*************************
Part 3: Analyzing Results
*************************

.. toctree::
   :maxdepth: 2

   simple_server/notebooks/simple_server_jupyter

.. toctree::
   :hidden:

   simple_server/using_elk.rst

*************************
Part 4: Adding Complexity
*************************

.. toctree::
   :maxdepth: 2

   simple_server/adding_topological_complexity.rst
