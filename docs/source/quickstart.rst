.. _quickstart-guide:

##########
Quickstart
##########

******************
Terminology Primer
******************
FIREWHEEL has some specific terminology, which is useful to understand prior to running any Emulytics experiments:

* An **Experiment** is the coordinated realization of your topology (e.g. live VMs) and the scheduled actions which occur within that realization. There are a number of reasons for running an experiment, so the outputs from the experiment differ depending on the use-case (e.g. live exercise vs software analysis). See :ref:`emulytics-introduction` for more details.
* In FIREWHEEL, an experiment is created via one or more **Model Components**. A :term:`Model Component` (MC) is a colocated set of related code, :term:`VM Resources`, and/or VM images. That is, model components are the building blocks of experiments. See :ref:`model_components` for a more detailed description.
* **VM Resources** (VMRs) can be any software or files, that runs on or otherwise interacts with running virtual machines in order to perform a desired function on them (e.g. install software, configure settings, collect data, etc.). :term:`VM Resources` are run via schedule, which users define in their Model Components. The VMR schedule is executed via the :ref:`vm_resource_system`.

.. TODO: Any missing key words?

********************
Installing FIREWHEEL
********************

While at it's core, FIREWHEEL is a Python package to realize cluster-based communications and emulation, the installation is more advanced than typical packages.
Because of the necessary configuration options, we recommend following the full installation guide :ref:`installing-FIREWHEEL`.
This quick start guide assumes that FIREWHEEL has been installed and is ready to be used.

***************
Getting Started
***************

We highly recommend reviewing our :ref:`FIREWHEEL-tutorials` for using FIREWHEEL.
After completing these tutorials, users should understand how to create and run a new experiment.

* :ref:`router-tree-tutorial` - Learn how to run an example topology with FIREWHEEL.
* :ref:`simple-server-tutorial` - Learn how to create a relatively simple experiment in which you will start a simple web server, grab a web page, and analyze the resulting data.

When building a new experiment, it's important to have realistic expectations about the complexity of building off-line Emulytics experiments.
While users have full access to the FIREWHEEL :ref:`Model Component library <available_model_components>`, they will likely need to code their own topologies and determine how to install/configure necessary experiment-related software in an offline-environment.
We recommend answering these questions before beginning a new experiment:

* What the topology should look like?

  * What VMs are needed?
  * How they should the VMs be connected?

*  What VM resources are needed?

   *  What software should be installed on the VMs and can it be installed in an offline-environment?
   *  How should the software be configured?
   *  How can the software installation/configuration be scripted/automated?

*  What data (if any) should be collected from the experiment?

   * How can that data be extracted from the experiment?


****************
Helpful Commands
****************

All the FIREWHEEL CLI commands are documented in :ref:`cli`, however, here are a few of the more used commands.

.. note::
    All the below commands should be prefaced with ``firewheel`` (e.g. ``firewheel experiment``).

* :ref:`helper_experiment` - The command how to execute model components and, thereby, start an experiment.
* :ref:`helper_vm_list` and :ref:`helper_vm_mix` - These commands help show the state of the currently running experiment. :ref:`helper_vm_list` has a number of options to show information about each VM.
* :ref:`helper_restart` - To end a running experiment and reset the testbed for a new experiment, run this command.
