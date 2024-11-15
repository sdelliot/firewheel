.. _vm_builder:

##########
VM Builder
##########

Often times, when building Model Components, it will be necessary to install some piece of external software.
Because FIREWHEEL VMs are entirely offline, all files and dependencies not pre-installed in the image must be stored as VM resources, dropped into the VM, and then installed.
This tutorial will go through the process of using the :ref:`helper_vm_builder` Helper to collect the Apache web server packages for a Ubuntu 22.04 VM.

The :ref:`helper_vm_builder` Helper enables users to launch/modify a single VM based on a passed in image file using minimega.
:ref:`VM Builder <helper_vm_builder>` is largely useful for preparing images for use with FIREWHEEL and as a testing ground for developing VM resources using the exact image that will be used within the experiment, as demonstrated by this tutorial.
Ultimately, it relies on `libvirt <https://libvirt.org/>`__ to provide automated networking to VMs, therefore, this package will need to be installed from wherever VM Builder is run, if it is not already.

.. warning::

    Currently, the automated installation of `libvirt <https://libvirt.org/>`__ only works on Debian-based systems (e.g., Ubuntu). All other systems will need to manually install this package.

Throughout this tutorial, you will follow the following basic steps:

1. Start VM Builder
2. Download dependencies in VM Builder
3. Copy all necessary files off of VM Builder and store as a Model Component's VM resources.
4. Configure the Model Component to install the packages.

.. seealso::
    The :ref:`offline-resources-tutorial` tutorial covers similar material, though does not necessarily assume the user is leveraging VM Builder for collecting resources.

*******************
Starting VM Builder
*******************

Assuming the default path for minimega's "files" directory (i.e., the :ref:`minimega.files_dir <config-minimega>` configuration option) directory for minimega, after running your first experiment, a cached copy of the ``qcow2`` images used for that experiment will be located in ``/tmp/minimega/files/images/``.
We recommend making a copy of this image to use for VM Builder to prevent any accidental modifications.
In this tutorial, we will be using a Ubuntu 22.04 image.

.. code-block:: bash

    $ cp /tmp/minimega/files/images/ubuntu-22.04-server-amd64.qcow2 /tmp/

Now, you can start VM Builder using the Helper.
For this example, we will choose to run the VM in ``launch`` mode to avoid modifying the ``qcow2`` image, we will allow networking, and we will give it 8 GB of RAM and 8 vCPUs:

.. code-block:: bash

    $ firewheel vm builder --launch --network --memory 8192 --vcpus 8 /tmp/ubuntu-22.04-server-amd64.qcow2
    VM started successfully. VNC port: 46469
    Connecting interface cdd52aa06a0c4dc to bridge virbr0
    Waiting for VM to be shut down...

At this point, you will be able to access the VM through miniweb's VNC interface (see :ref:`router-tree-miniweb` for additional help).
In a browser, go to ``localhost:9001`` and find the newly launched VM.

.. note::
    If running FIREWHEEL on a remote server, you can ``ssh`` to it with ``ssh -L9001:localhost:9001 <server_name>`` to forward port 9001 to a local machine.


Downloading Dependencies
*************************

Inside of VM builder, you will need to obtain network access by using:

.. code-block:: bash

    $ sudo dhclient

.. note::
    For Ubuntu 24.04 (and likely anything newer) you can use ``dhcpcd <interface-name>`` instead. For example, ``dhcpcd ens5``.

You can verify this worked by running the following command and making sure an IP address appears in the output:

.. code-block:: bash

    $ ifconfig

At this point, you should ensure any necessary proxy environment variables are set.
Then, download the dependencies and save them.
To install ``apache``, we will run:

.. code-block:: bash

    $ sudo apt-get update
    $ sudo apt-get install -y apache2

.. warning::

    It is **very important** that you use ``apt-get`` and not just ``apt``. See :ref:`offline-ubuntu` for more details on collecting packages on Ubuntu systems for later use within a FIREWHEEL experiment.

Now, the ``.deb`` packages for ``apache2`` will be located in ``/var/cache/apt/archives``.
So we'll copy them into their own folder and create a tarball.

.. code-block:: bash

    $ mkdir /home/ubuntu/apache2-debs
    $ cp /var/cache/apt/archives/*.deb /home/ubuntu/apache2-debs
    $ cd /home/ubuntu
    $ tar -czvf apache2-debs.tgz apache2-debs/


Save off files, Configure Model Component
******************************************

Now, we will ``scp`` the files off of the VM and store them as VM resources in our new Model Component.
So, from the server that launched VM Builder, run:

.. code-block:: bash

    $ scp ubuntu@192.168.122.234:/home/ubuntu/apache2-debs.tgz /tmp

.. note::

    It is possible that the IP address before may differ, you can run ``ifconfig`` to verify.

You can then copy the tarball into a new or existing model component, and make sure to add it as a VM resource in the ``MANIFEST`` file.
Then, adding the following line to a ``model_component_objects.py`` file will install the ``apache2`` debian package inside the VM at time ``-70``:

.. code-block:: python

    self.install_debs(-70, "apache2-debs.tgz")

Depending on the package, there may be other configuration that will also need to be done.
For example, this will install the ``apache`` software, but does not configure an actual website, which is out of scope for this tutorial and can be done through other ``vm_resources``.

Ultimately, VM Builder (or a similar tool) is critical to developing high-fidelity experiments within an offline environment.
To learn more about configuring experiments see :ref:`offline-resources-tutorial`.
