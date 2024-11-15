Creating a Model Component for a New Image
------------------------------------------

For a quick refresher on what a model component is, see :ref:`model_components`.
You can also review the model components that were created in the ACME repository.
In the model component that this tutorial builds, we are going to focus on create a model component that provides objects to plugins.

Generating a Model Component Skeleton
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a directory for our model component within a repository and then run the ``firewheel mc generate`` function with the appropriate parameters.
Since we're building an ``Ubuntu Server`` it makes sense to place this model component in the ``linux`` repository: ::

    $ mkdir -p /opt/firewheel/model_components/linux/ubuntu/cosmic
    $ mv ubuntu-18.10-server-amd64.qcow2.xz /opt/firewheel/model_components/linux/ubuntu/cosmic
    $ firewheel mc generate --name linux.ubuntu1810 \
        --location /opt/firewheel/linux/ubuntu/cosmic \
        --image ubuntu-18.10-server-amd64.qcow2.xz \
        --arch x86_64 \
        --model_component_depends linux.ubuntu \
        --model_component_objects model_component_objects.py

We'll walk through the parameters:

* ``name``: Choose the name of the model component. In this case we use ``linux.ubuntu1810``.
* ``location``: The absolute path the directory that should contain this model component.
* ``image``: The path (relative to the model component) to the image file that was created in :ref:`building_iso`. In this case it is expected that the disk image lives within the ``cosmic`` directory.
* ``model_component_depends``: We want to be able to use all the functions that a base Linux VM provides, therefore we depend on ``linux.base_objects``.
* ``model_component_objects``: This specifies the name of the file that holds the objects that we want to provide to a topology. It can be named anything you like, but we have found that using ``model_component_objects.py`` is a reasonable convention to follow.

As mentioned above, this model component assumes that the ``ubuntu-18.10-server-amd64.qcow2.xz`` file is located within the ``cosmic`` directory.
It is best to have the image within the model component because then everything associated with the component is in one place.
You should now see all the relevant model component files in ``/opt/firewheel/linux/ubuntu/cosmic``.

Creating the ``Ubuntu1810Server`` object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``MANIFEST`` file defined that the model component objects are located in a file called ``model_component_objects.py``.
Create that file to look as follows: ::

    from firewheel.control.experiment_graph import require_class
    from linux.ubuntu import UbuntuServer

    @require_class(UbuntuServer)
    class Ubuntu1810Server(object):
        def __init__(self):
            try:
                self.vm
            except AttributeError:
                self.vm = {}

            if 'architecture' not in self.vm:
                self.vm['architecture'] = 'x86_64'
            if 'vcpu' not in self.vm:
                self.vm['vcpu'] = {
                    'model': 'qemu64',
                    'sockets': 1,
                    'cores': 1,
                    'threads': 1
                }
            if 'mem' not in self.vm:
                self.vm['mem'] = 256
            if 'drives' not in self.vm:
                self.vm['drives'] = [
                    {
                        'db_path': 'ubuntu-18.10-server-amd64.qcow2.xz',
                        'file': 'ubuntu-18.10-server-amd64.qcow2'
                    }
                ]
            if 'vga' not in self.vm:
                self.vm['vga'] = 'std'

            self.set_image('ubuntu1810server')

Let's walk through the object.
First, we import two things, ``require_class`` and ``UbuntuServer``.
The ``require_class`` function is a decorator that we use to indicate inter-class dependencies.
So, in this case, we're saying that the ``Ubuntu1810Server`` class requires the ``UbuntuServer`` class.
You can think of this as reverse inheritance.
In inheritance, the object being instantiated gets to run first and passes control to its parent through a call to ``super()``.
When using the ``require_class`` decorator it gives control to the object that is required before handing it over to the object being instantiated.
Similar to inheritance, any function that is defined in ``UbuntuServer`` is available to ``Ubuntu1810Server``.
This allows us to create "layers" that can be "stacked" in different ways to make complex objects.
It also allows us to define functions at an appropriate layer so that they can have the widest possible usage.
Therefore, ``UbuntuServer`` has functions that are relevant to any image that uses Ubuntu Server as well as any model components that are higher in the stack.
An example of such a function is ``configure_ips()``.
The ``configure_ips()`` function in the ``LinuxHost`` object will ensure that the correct commands get run on a Linux VM to set its IP address.
This differs from the ``configure_ips()`` function in the ``WindowsHost`` object since the mechanism for setting an IP on Windows is different than on Linux.
The ``UbuntuServer`` class requires ``UbuntuHost`` which requires ``LinuxHost``
Therefore, we can require the ``LinuxHost`` class from many different objects and duplicating effort.
We recommend that you use the most specific class to enable all available functions.
For example, the ``UbuntuHost``, which ``UbuntuServer`` requires, contains the ``install_debs()`` function which installs Debian packages.

Next, we check to see if the ``vm`` variable already exists on the object.
Remember, decorators are reversed from inheritance in the sense that the required classes are executed first.
Therefore, we have to be careful not to accidentally undo things previous "layers" did unless it is intended.
Once the ``vm`` dictionary is present, we set parameters such as ``architecture``, ``vcpu``, ``mem``, ``drives``, and ``vga``.
Feel free to change any of these values to fit the needs of the image that is being created.
Note that ``db_path`` needs to be the same as the ``paths`` parameter that was set in the ``MANIFEST`` file.
The ``file`` parameter allows the name of the decompressed disk to be something different than the base name of the compressed disk, although it is doubtful that they'll be different in most cases (other than the ``xz`` suffix of course).

The ``set_image()`` function takes an arbitrary string.
Feel free to set it to anything that you like, but it is good convention to make it consistent with the name of the class.
This value tells ``FIREWHEEL`` that the VM decorated by this class does not need a default image because we're explicitly setting its image type in the class.

At this point this class is usable within a topology.
All that a topology would need to do is import this class via ``from linux.ubuntu1810 import Ubuntu1810Server`` and to decorate a vertex with the ``Ubuntu1810Server`` class.
Don't forget to add ``linux.ubuntu1810`` as a model component dependency in the topology model component's ``MANIFEST`` file.
