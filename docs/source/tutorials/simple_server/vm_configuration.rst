.. _simple-server-vm_configuration:

**************************
Preparing for VM resources
**************************

Now that the topology has been created and works, we can start automating the experiment actions.
In FIREWHEEL, we use the term *VM Resources* as a catch-all term for any automated actions which modify the experiment after the VMs start.
This could include VM configuration changes, installing new software, or automating some action.
In this experiment, we will want the ``Server`` to have the following VM resources:

1.  A Python web server running from a specific directory.
2.  A file located in that specific directory.

The ``Client`` will need the following VM resource:

1. A script to download a file from the server.

.. seealso::

    For more information, please refer to the :ref:`vm_resource_system` documentation.

To prepare for adding these new VM resources, we need to add the ``vm_resources`` field to our MANIFEST file (see :ref:`vm_resources_field`).
To make it easy, we will create a new folder in the ``simple_server`` Model Component folder called "vm_resources":

.. code-block:: bash

    $ mkdir vm_resources

Now open the MANIFEST file and add the lines:

.. code-block:: yaml

    vm_resources:
        - vm_resources/*

Now all files located in the "vm_resources" folder will automatically be available to use as a VM resource.

.. note::

    For general information on using VM resources in FIREWHEEL see :ref:`using-vm-resources`.

************************************
Using ``model_component_objects.py``
************************************
We can easily schedule our VM resources in ``plugin.py``, however, as the complexity of the experiment grows, code readability decreases.
Therefore, we will be using the ``model_component_objects.py`` file to create new Objects for our Server and Client.

Open the ``model_component_objects.py`` file.
It should look like:

.. code-block:: python

    """This module contains all necessary Model Component Objects for tutorials.simple_server."""

    from firewheel.control.experiment_graph import require_class

    class MyObject:
        """MyObject Class documentation."""

        def __init__(self):
            # TODO: Implement Class constructor here
            pass

Creating the Server Object
==========================
We will modify that first object to create the Server.
First rename "MyObject" to "SimpleServer".

.. code-block:: python

    class SimpleServer:

Next, we want the Server to be a :py:class:`Ubuntu1604Server <linux.ubuntu1604>`.
In the Plugin, we simply decorated the server with the correct object.
In the Model Component Objects file, there is an alternative approach.
You can use FIREWHEEL's :py:meth:`require_class <firewheel.control.experiment_graph.require_class>` decorator to decorate
the object with the correct class.
In this case, we will first need to import :py:class:`Ubuntu1604Server <linux.ubuntu1604>` then decorate our ``SimpleServer`` object.

.. code-block:: python

    from linux.ubuntu1604 import Ubuntu1604Server

    @require_class(Ubuntu1604Server)
    class SimpleServer:

Creating the Client Object
==========================

Initially, client object will be the same as the ``SimpleServer`` object and will also be added to the ``model_component_objects.py`` file.

It should look like:

.. code-block:: python

    @require_class(Ubuntu1604Server)
    class SimpleClient:
        """SimpleClient Class documentation."""

        def __init__(self):
            # TODO: Implement Class constructor here
            pass


Updating the Plugin
===================
Now we can update the Plugin to use the newly created objects.
Open ``plugin.py``.
First we will import our new object and remove the import statement for ``Ubuntu1604Server``, which is no longer needed.
Then we can decorate our client/server with the newly created objects.
The new plugin will look like:

.. code-block:: python
    :emphasize-lines: 4,13,27

    from firewheel.control.experiment_graph import AbstractPlugin, Vertex

    from base_objects import Switch
    from tutorials.simple_server import SimpleServer, SimpleClient

    class Plugin(AbstractPlugin):
        """tutorials.simple_server plugin documentation."""

        def run(self):
            """Run method documentation."""
            # Create the Server
            server = Vertex(self.g, name="Server")
            server.decorate(SimpleServer)

            # Create the switch
            switch = Vertex(self.g, name="Switch")
            switch.decorate(Switch)

            # Connect the server and the switch
            server.connect(
                switch,  # The Switch Vertex
                "1.0.0.1",  # The IP address for the server
                "255.255.255.0"  # The subnet mask for the IP address network
            )

            # Create the client
            client = Vertex(self.g, name="Client")
            client.decorate(SimpleClient)

            # Connect the client and the switch
            client.connect(
                switch,  # The Switch Vertex
                "1.0.0.2",  # The IP address for the client
                "255.255.255.0"  # The subnet mask for the IP address network
            )

***********************
Adding the VM Resources
***********************
Now that we have a new structure, we can schedule all of our VM resources in ``model_component_objects.py`` and no longer have to update the Plugin.

Adding the Server's VMRs
========================

Creating a File
---------------

First, we need to create a file for the client to pull.
To do this, we will just generate a new 50MB file, and put it in our ``vm_resources`` folder.

Open up ``model_component_objects.py``.
It's best to create a new method in the ``SimpleServer`` object for this functionality.
To create this file we will use the :py:func:`os.urandom` method to generate random data which can be written to a file.
We will name the file ``file.txt``.
The initial method will look like:

.. code-block:: python

    def configure_files_to_serve(self, file_size=52428800):
        """
        Generate a file that is of size ``file_size`` (e.g. default of 50MB) and drop it on the VM.

        Args:
            file_size (int): The size of the file to create. By default it is 50MB.
        """
        # Get the current executing directory
        current_module_path = os.path.abspath(os.path.dirname(__file__))

        # Create a path to the soon-to-be-created file
        filename = "file.txt"
        path = os.path.join(current_module_path, "vm_resources", filename)

        # Generate the random data which will fill the file
        random_bytes = os.urandom(file_size)

        # Write the file to disk
        with open(path, "wb") as fout:
            fout.write(random_bytes)

Now that we can generate a file, we need to add it to the VM.
We will use the :py:meth:`drop_file <base_objects.VMEndpoint.drop_file>` method to do so.
In this case, we will place ``file.txt`` in ``/opt/file.txt`` on the Server VM.
Additionally, we will want this file placed in the VM during :ref:`schedule-negative-time` as this part of the experiment is used primarily for configuration of the VMs.
Add the following to the newly created method.

.. code-block:: python

    # Drop the new file onto the VM.
    self.drop_file(
        -5,  # The experiment time to add the content. (i.e. during configuration)
        f"/opt/{filename}",  # The location on the VM of the file to drop
        filename  # The filename of the newly created file on the physical host.
    )

Lastly, because we always want this method to run, we will add it to the Object's ``init()`` method.

.. code-block:: python

    @require_class(Ubuntu1604Server)
    class SimpleServer:
        """SimpleServer Class documentation."""

        def __init__(self):
            self.configure_files_to_serve()


Running The Server
------------------
For our web server, we will use the :py:mod:`http.server` module.
Additionally, we will want to start the server in the ``/opt`` directory on the VM so that it will have access to the newly created ``file.txt``.

To make all of those actions happen, we can use the following line in bash.

.. code-block:: bash

    bash -c 'pushd /opt; python3 -m http.server; popd'

.. warning::

    When running a VM Resource, be mindful of what implicit environment variables are needed.
    Ignoring these assumptions can cause issues.
    See :ref:`vmr-env` for more information.

To schedule this action, we will use the :py:meth:`run_executable <base_objects.VMEndpoint.run_executable>` method.
We want the :ref:`start-time` for the VMR to be as soon as the experiment is configured (e.g. 1 second after the experiment is configured).
In the ``init()`` method, add the following lines:

.. code-block:: python

    # Start the web server at time=1
    # The server needs to run in the ``/opt`` directory because that is where the
    # file will be located.
    self.run_executable(
        1,  # The experiment time to run this program (e.g. 1 second after start).
        "bash",  # The name of the executable program to run.
        arguments="-c 'pushd /opt; python3 -m http.server; popd'"  # The arguments for the program.
    )

The full ``SimpleServer`` Object should now look like:

.. code-block:: python

    @require_class(Ubuntu1604Server)
    class SimpleServer:
        """SimpleServer Class documentation."""

        def __init__(self):
            self.configure_files_to_serve()

            # Start the web server at time=1
            # The server needs to run in the ``/opt`` directory because that is where the
            # file will be located.
            self.run_executable(
                1,  # The experiment time to run this program (e.g. 1 second after start).
                "bash",  # The name of the executable program to run.
                arguments="-c 'pushd /opt; python3 -m http.server; popd'"  # The arguments for the program.
            )

        def configure_files_to_serve(self, file_size=52428800):
            """Generate a file that is of size ``file_size`` (e.g. 50MB) and drop it on the VM.

            Args:
                file_size (int): The size of the file to create. By default it is 50MB.
            """
            # Get the current executing directory
            current_module_path = os.path.abspath(os.path.dirname(__file__))

            # Create a path to the soon-to-be-created file
            filename = "file.txt"
            path = os.path.join(current_module_path, "vm_resources", filename)

            # Generate the random data which will fill the file
            random_bytes = os.urandom(file_size)

            # Write the file to disk
            with open(path, "wb") as fout:
                fout.write(random_bytes)

            # Drop the new file onto the VM.
            self.drop_file(
                -5,  # The experiment time to add the content. (i.e. during configuration)
                f"/opt/{filename}",  # The location on the VM of the file to drop
                filename  # The filename of the newly created file on the physical host.
            )

Adding the Client's VMRs
========================

The client is responsible for requesting the file from the web server and calculating how much time it took.
Because we need to measure the download speed, we need to be thoughtful about how to present the resulting data.
There are several methods for getting data out of an experiment.
We can pull specific files out of the experiment using either the :ref:`helper_pull_file` CLI command, we can schedule file extraction using the :py:meth:`file_transfer <base_objects.VMEndpoint.file_transfer>` method, or we can use the automatically extracted VM resource ``stdout`` as detailed in :ref:`vmr-output`.
In this case, we will opt to use the output from our VM resources (see :ref:`manual-interaction` for more details on the other methods).
Additionally, because we want to visualize the data, we will ensure that it is in JSON format.

As it turns out, the `cURL <https://curl.se/>`_ command has the ability to write output in a specific format.
Therefore, we will use this feature (the ``-w`` flag) to help grab the download time.

To make use of this flag we will first drop our format string into a file on the VM, then we will run cURL on the VM using the ``-w`` flag.
Lastly, before we can cURL, we will need to know the IP address of the server.

Grabbing the File
-----------------

Open ``model_component_objects.py`` to begin editing the ``SimpleClient``.
We will begin by adding a new method to this object which takes in the Server's IP address.
This method will run cURL and output our desired results.

.. code-block:: python

    @require_class(Ubuntu1604Server)
    class SimpleClient:
        """SimpleClient Class documentation."""

        def __init__(self):
            pass

        def grab_file(self, server_ip):
            # Drop the cURL format string
            pass

Remember, that we want the total download time in JSON format.
That is, our output should look like: ``{"time": "0.206"}``.
We will be dropping this content into a file on the VM using the :py:meth:`drop_content <base_objects.VMEndpoint.drop_content>` method.

.. code-block:: python

    def grab_file(self, server_ip):
        # Drop the cURL format string
        self.drop_content(
            -5,  # The experiment time to add the content. (i.e. during configuration)
            "/opt/curl_format.txt",  # The location on the VM of the file
            '{"time":"%{time_total}"}\\n'  # The content to add to the file.
        )

Now we can call cURL to use this format and grab the file from the server.
The :ref:`start-time` for the cURL command will be ``10`` (e.g. ten seconds after the entire experiment has been configured) because we want to allow some buffer time for the Server to start.

.. code-block:: python

    def grab_file(self, server_ip):
        # Drop the cURL format string
        self.drop_content(
            -5,  # The experiment time to add the content. (i.e. during configuration)
            "/opt/curl_format.txt",  # The location on the VM of the file
            '{"time":"%{time_total}"}\\n'  # The content to add to the file.
        )

        # Run cURL command
        self.run_executable(
            10,  # The experiment time to run this program (e.g. 10 seconds after start).
            "/usr/bin/curl",  # The name of the executable program to run.
            arguments=f'-w "@/opt/curl_format.txt" -O {server_ip}:8000/file.txt',
        )

.. note::
    It is best practice to use the full path of the binary being executed.

Now that our VM resources are in place, we need to update our plugin to call this method and pass in the Server's IP address.

Updating the Plugin
-------------------
Open ``plugin.py``.
First, we will want to replace the hard-coded IP address of the server with a variable.
It should now look like this:

.. code-block:: python

    # Connect the server and the switch
    server_ip = "1.0.0.1"
    server.connect(
        switch,  # The Switch Vertex
        server_ip,  # The IP address for the server
        "255.255.255.0"  # The subnet mask for the IP address network
    )

Lastly, at the end of the Plugin, have the client call the newly created ``grab_file`` method and pass in ``server_ip``.

.. code-block:: python

    client.grab_file(server_ip)

Ensuring it works
=================
Once all the updates have been made, restart your experiment to identify any syntax errors which might have been made.
In the next section we will learn how to analyze the output from our VMRs.

Completed ``model_component_objects.py``
========================================

.. code-block:: python

    """This module contains all necessary Model Component Objects for tutorials.simple_server."""
    import os

    from firewheel.control.experiment_graph import require_class

    from linux.ubuntu1604 import Ubuntu1604Server


    @require_class(Ubuntu1604Server)
    class SimpleServer:
        """SimpleServer Class documentation."""

        def __init__(self):
            self.configure_files_to_serve()

            # Start the web server at time=1
            # The server needs to run in the ``/opt`` directory because that is where the
            # file will be located.
            self.run_executable(
                1, "bash", arguments="-c 'pushd /opt; python3 -m http.server; popd'"
            )

        def configure_files_to_serve(self, file_size=52428800):
            """
            Generate a file that is of size ``file_size`` (e.g. default of 50MB) and drop it on the VM.

            Args:
                file_size (int): The size of the file to create. By default it is 50MB.
            """
            # Get the current executing directory
            current_module_path = os.path.abspath(os.path.dirname(__file__))

            # Create a path to the soon-to-be-created file
            filename = "file.txt"
            path = os.path.join(current_module_path, "vm_resources", filename)

            # Generate the random data which will fill the file
            random_bytes = os.urandom(file_size)

            # Write the file to disk
            with open(path, "wb") as fout:
                fout.write(random_bytes)

            # Drop the new file onto the VM.
            self.drop_file(
                -5,  # The experiment time to add the content. (i.e. during configuration)
                f"/opt/{filename}",  # The location on the VM of the file to drop
                filename  # The filename of the newly created file on the physical host.
            )


    @require_class(Ubuntu1604Server)
    class SimpleClient:
        """SimpleClient Class documentation."""

        def __init__(self):
            pass

        def grab_file(self, server_ip):
            """
            Add a curl format to the VM and then run our ``fetch_file.sh`` VM resource
            which will attempt to curl the file from the server and record the time.
            """
            # Drop the cURL format string
            self.drop_content(
                -5,  # The experiment time to add the content. (i.e. during configuration)
                "/opt/curl_format.txt",  # The location on the VM of the file
                '{"time":"%{time_total}"}\\n'  # The content to add to the file.
            )

            # Run cURL command
            self.run_executable(
                10,  # The experiment time to run this program (e.g. 10 seconds after start).
                "/usr/bin/curl",  # The name of the executable program to run.
                arguments=f'-w "@/opt/curl_format.txt" -O {server_ip}:8000/file.txt',
            )

Completed ``plugin.py``
=======================

.. code-block:: python

    from firewheel.control.experiment_graph import AbstractPlugin, Vertex

    from base_objects import Switch
    from tutorials.simple_server import SimpleServer, SimpleClient

    class Plugin(AbstractPlugin):
        """tutorials.simple_server plugin documentation."""

        def run(self):
            """Run method documentation."""
            # Create the Server
            server = Vertex(self.g, name="Server")
            server.decorate(SimpleServer)

            # Create the switch
            switch = Vertex(self.g, name="Switch")
            switch.decorate(Switch)

            # Connect the server and the switch
            server_ip = "1.0.0.1"
            server.connect(
                switch,  # The Switch Vertex
                server_ip,  # The IP address for the server
                "255.255.255.0"  # The subnet mask for the IP address network
            )

            # Create the client
            client = Vertex(self.g, name="Client")
            client.decorate(SimpleClient)

            # Connect the client and the switch
            client.connect(
                switch,  # The Switch Vertex
                "1.0.0.2",  # The IP address for the client
                "255.255.255.0"  # The subnet mask for the IP address network
            )

            client.grab_file(server_ip)
