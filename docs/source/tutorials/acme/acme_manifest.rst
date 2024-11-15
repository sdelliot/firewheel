.. _acme-topo-mc-generation:

*************************************
Creating the Topology Model Component
*************************************

In most cases the fastest and easiest way to build a model component is going to be done by utilizing the :ref:`helper_mc_generate` command.
The command can take a handful of parameters and generate a model component skeleton from that information.
Alternatively, users can interactively use the command.
We will want to set the following parameters:

* ``name=acme.topology`` -- The model component needs a name. In this case, a sensible option is ``acme.topology``.
* ``attribute_depends=graph`` -- To add new Vertices to the graph, we first need to ensure the graph has been created. Therefore, this model component will depend on the ``graph`` attribute.
* ``attribute_provides=topology`` -- This is a topology file, so we're going to be a provider of a ``topology``.
* ``model_component_depends=base_objects linux.ubuntu2204 vyos.helium118`` -- As mentioned in :ref:`acme-getting-started`, we will need these MCs to properly create our topology.
* ``plugin=plugin.py`` -- Plugin files are used to manipulate the graph (see :ref:`plugin_field`). Therefore, we will need to specify the name of the plugin file that needs to be run to actually generate the topology. We suggest always naming this file ``plugin.py`` for consistency.
* ``location=acme/topology`` -- The location of the topology MC. Note that the generation command will automatically create any necessary directories.

In order to create the skeleton for the topology model component, run the following::

    $ firewheel mc generate

    (name) ModelComponent name : acme.topology
    (attribute_depends) (space-separated-strings) Graph Attribute(s) depended on by the new ModelComponent []: graph
    (attribute_provides) (space-separated-strings) Graph Attribute(s) provided by the new ModelComponent []: topology
    (attribute_precedes) (space-separated-strings) Graph Attribute(s) preceded by the new ModelComponent []:
    (model_component_depends) (space-separated-strings) ModelComponent(s) required by name []: base_objects linux.ubuntu2204 vyos.helium118
    (model_component_precedes) (space-separated-strings) ModelComponent(s) that will be preceded by name []:
    (plugin) File for a plugin []: plugin.py
    (model_component_objects) File for Model Component Objects []:
    (location) Location for the new ModelComponent : acme/topology
    (vm_resources) (space-separated-strings) File(s) to be used as a vm_resource []:
    (image) File to be used as a VM disk []:
    (arch) Architecture for specified image []:

Upon completion of this command, it will create the necessary files needed to get started with creating your topology.

* ``MANIFEST`` - The basis for every model component is its ``MANIFEST`` file.
  If you are not familiar with FIREWHEEL ``MANIFEST`` files then it is recommended that you read :ref:`manifest_file` before continuing this tutorial.
  Our ``MANIFEST`` file will look like:

  .. code-block:: yaml

    attributes:
        depends:
        - graph
        precedes: []
        provides:
        - topology
    model_components:
        depends:
        - base_objects
        - linux.ubuntu2204
        - vyos.helium118
        precedes: []
    name: acme.topology
    plugin: plugin.py

* ``plugin.py`` - A template for our Plugin.
  This is where all of the logic will happen for our MC.
* ``README.rst`` - We always recommend writing good documentation about your MC to facilitate reusability.
* ``INSTALL`` - An empty template for developers to get any necessary external components needed for the model component.
