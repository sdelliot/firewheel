.. _FIREWHEEL-experiments:

FIREWHEEL Experiments
=====================

A FIREWHEEL experiment is simply a collection of model components which, when combined, define everything about an experiment.
The model components that make up an experiment define its network topology, which can include:

    * Its vertices, which will become computing, networking, or other device VMs
    * The edges that represent network connections amongst the vertices
    * Vertex and edge class types that can be assigned to individual vertices
    * The VM images associated with the various vertex class types
    * VM resource files that will alter the state of a VM once booted
    * Scheduling info for when and where those VM resources will modify the VM

FIREWHEEL's model components depend on one another to provide reusable, modular building blocks for constructing a wide variety of LAN, WAN, or even Internet scale experiments.

Once all the model components are executed, the experiment graph (via NetworkX) is able to be compiled into a running experiment via simulation, emulation, or physical hardware.
Currently, using emulation via minimega is the only supported experimentation method, in future versions of FIREWHEEL there may be other methods in which users can instantiate an experiment.

The remainder of this section outlines FIREWHEEL's dependency management system.

.. toctree::
   :maxdepth: 3

   dependencies
