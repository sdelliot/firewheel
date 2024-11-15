.. _simple-server-mc-generation:

*************************************
Creating the Topology Model Component
*************************************

In most cases the fastest and easiest way to build a Model Component is going to be done by utilizing the :ref:`helper_mc_generate` command.
The command can take a handful of parameters and generate a Model Component skeleton from that information.
Alternatively, users can interactively use the command.
We will want to set the following parameters:

* ``name=tutorials.simple_server`` -- The Model Component needs a name. In this case, a sensible option is ``tutorials.simple_server``.
* ``attribute_depends=graph`` -- To add new Vertices to the graph, we first need to ensure the graph has been created. Therefore, this Model Component will depend on the ``graph`` attribute.
* ``attribute_provides=topology`` -- This is a topology file, so we're going to be a provider of a ``topology``.
* ``model_component_depends=base_objects linux.ubuntu1604`` -- As mentioned in :ref:`simple-server-getting-started`, we will need these MCs to properly create our topology.
* ``plugin=plugin.py`` -- Plugin files are used to manipulate the graph (see :ref:`plugin_field`). Therefore, we will need to specify the name of the plugin file that needs to be run to actually generate the topology. We suggest always naming this file ``plugin.py`` for consistency.
* ``model_component_objects=model_component_objects.py`` -- Model component objects files contain Python objects which can be used to decorate different graph vertices and edges (see :ref:`model_component_objects_field`). Therefore, we will need to specify the name of the Model Component objects file that will be imported. We suggest always naming this file ``model_component_objects.py`` for consistency.
* ``location=/opt/firewheel/model_components/simple_server`` -- The location of the topology MC. Note that the generation command will automatically create any necessary directories.

Other parameters (e.g. ``attribute_precedes``, ``image``, etc.) can be ignored and you can just press the "return" key when prompted.
In order to create the skeleton for the topology Model Component, run the following:

.. code-block:: bash

    $ firewheel mc generate
    (name) ModelComponent name : tutorials.simple_server
    (attribute_depends) (space-separated-strings) Graph Attribute(s) depended on by the new ModelComponent []: graph
    (attribute_provides) (space-separated-strings) Graph Attribute(s) provided by the new ModelComponent []: topology
    (attribute_precedes) (space-separated-strings) Graph Attribute(s) preceded by the new ModelComponent []:
    (model_component_depends) (space-separated-strings) ModelComponent(s) required by name []: base_objects linux.ubuntu1604
    (model_component_precedes) (space-separated-strings) ModelComponent(s) that will be preceded by name []:
    (plugin) File for a plugin []: plugin.py
    (model_component_objects) File for Model Component Objects []: model_component_objects.py
    (location) Location for the new ModelComponent : /opt/firewheel/model_components/simple_server
    (vm_resources) (space-separated-strings) File(s) to be used as a vm_resource []:
    (image) File to be used as a VM disk []:
    (arch) Architecture for specified image []:

.. note::
  The :ref:`helper_mc_generate` helper can also be used non-interactively. For example, to create the same MC outline, you can use the command::

    $ firewheel mc generate --non-interactive --name tutorials.simple_server --attribute_depends graph --attribute_provides topology --model_component_depends base_objects linux.ubuntu1604 --plugin plugin.py --model_component_objects model_component_objects.py --location /opt/firewheel/model_components/simple_server

.. note::
    If you chose to use a path other than ``/opt/firewheel/model_components`` you will need to install that path as a FIREWHEEL repository (see :ref:`repository-creation`).

Upon completion of this command, it will create the necessary files needed to get started with creating your topology.

* ``MANIFEST`` - The basis for every Model Component is its ``MANIFEST`` file.
  If you are not familiar with FIREWHEEL ``MANIFEST`` files then it is recommended that you read :ref:`manifest_file` before continuing this tutorial.
  Our ``MANIFEST`` file will look like:

  .. code-block:: yaml

    attributes:
      depends:
      - graph
      precedes: []
      provides:
      - topology
    model_component_objects: model_component_objects.py
    model_components:
      depends:
      - base_objects
      - linux.ubuntu1604
      precedes: []
    name: tutorials.simple_server
    plugin: plugin.py

* ``model_component_objects.py`` - A template for our Model Component objects.
* ``plugin.py`` - A template for our Plugin.
  This is where the primary logic will happen for our MC.
* ``README.rst`` - We always recommend writing good documentation about your MC to facilitate reusability.
