.. _manual-interaction:

*************************
Data Transfer/Interaction
*************************

For this tutorial, we have primarily used FIREWHEEL's automated VM resource logging to extract the experimental results.
However, there are plenty of use cases where someone might need to move data (i.e. files or tarballs) in or out of a VM that is part of a running experiment.

In this module, we will explore a few alternate methods for interacting with your experimental results.
There are currently two ways to interact "on-demand" and two ways to do so programmatically.
As an example, we will assume that the user also wants to collect and analyze the ``/etc/hosts`` file for each VM.


Manual Extraction
=================

Using :ref:`helper_pull_file`
-----------------------------
The easiest method for grabbing a file (or files) from a VM in a running experiment is to use the :ref:`helper_pull_file` command.
This command does not require that VMs are running an SSH server and does not need to use the :ref:`control_network_mc`.
See the :ref:`helper_pull_file` documentation for more information.

To grab the ``/etc/hosts`` file from the server, we can run the following command:

.. code-block:: bash

    $ firewheel pull file /etc/hosts Server /tmp/data/hosts.txt
    hosts                         100%  176     0.2KB/s   00:00


The arguments are:
   * ``/etc/hosts`` - The name of the file or directory on the VM to pull back.
   * ``Server`` - The hostname of the VM to pull the files from.
   * ``/tmp/data/hosts.txt`` - Local destination path for the files that were pulled from the VM.

The file will now be downloaded and located at ``/tmp/data/hosts.txt`` on your compute node.

Using :ref:`helper_scp`
-----------------------

To use the :ref:`helper_scp` CLI command, you will first need to plan ahead prior to launching your experiment.
That is, this command will only work if the :ref:`control_network_mc` model component is used.
Therefore, restart your experiment using this Model Component:

.. code-block:: bash

   $ firewheel experiment -r tutorials.simple_server control_network minimega.launch

This MC will add a new network interface to each VM and connect them to the :ref:`cluster-control-node`, so that the VMs can interact with the physical host.

Once the experiment has launched users can use the :ref:`helper_scp` CLI command to `secure copy (scp) <https://linux.die.net/man/1/scp>`_ files to or from VMs which are running an SSH server.
By default, Ubuntu Desktop images may **NOT** be running an SSH server.

The FIREWHEEL-specific SCP traffic is proxied through the compute server and directed at the control interface for each VM.
The command takes the same form as standard ``scp``, except for the ``firewheel`` keyword at the beginning:

.. code-block:: bash

    $ firewheel scp <user>@<VM hostname>:<VM path> <local path>
    $ firewheel scp <local path> <user>@<VM hostname>:<VM path>

Continuing our example above, we will show how to pull the ``/etc/hosts`` file from the Server:

.. code-block:: bash

   $ firewheel scp ubuntu@Server:/etc/hosts /tmp/data/hosts.txt
   PING 172.16.0.2 (172.16.0.2) 56(84) bytes of data.
   64 bytes from 172.16.0.2: icmp_seq=1 ttl=64 time=1.08 ms

   --- 172.16.0.2 ping statistics ---
   1 packets transmitted, 1 received, 0% packet loss, time 0ms
   rtt min/avg/max/mdev = 1.081/1.081/1.081/0.000 ms
   ubuntu@172.16.0.2's password:
   hosts                     100%  176     0.2KB/s   00:00

.. note::
   The :ref:`helper_scp` and :ref:`helper_ssh` commands will ping the VM first to ensure that the :ref:`control_network_mc` is active.

The file will now be downloaded and located at ``/tmp/data/hosts.txt`` on your control node.

.. note::
    All standard `scp <https://linux.die.net/man/1/scp>`_ options are available to the FIREWHEEL version of ``scp``.
    Options simply get passed on to the underlying command.


Automating File Extraction
==========================
If it is known that specific data needs to be retrieved from a VM when the topology is created then it can be done programmatically.
Files that are retrieved programmatically can either be retrieved once or on an interval.
The two methods that provide this capability are :py:meth:`file_transfer_once <base_objects.VMEndpoint.file_transfer_once>` and :py:meth:`file_transfer <base_objects.VMEndpoint.file_transfer>`.

For example, pulling the ``/etc/hosts`` file every two minutes from the Server would require adding the following lines to our ``plugin.py`` (in the ``run()`` method):

.. code-block:: python

   server.file_transfer(
      "/etc/hosts",  # The location of the file in the VM.
      120,  # The number of seconds between pulling the file.
      start_time=5  # Starting 5 seconds into the experiment.
   )

Files retrieved programmatically are placed on the compute server hosting the VM at ``/scratch/transfers/<VM hostname>/<file path>``.

.. note::
    When files are retrieved on an interval for Linux based VMs, only files that have changed since the last interval are actually pulled off the VM.
    Currently, Windows VMs will pull the file at every interval regardless of whether or not the file has changed since the last retrieval.


*************************
Non-GUI Based Interaction
*************************

For users that would prefer to not use VNC/miniweb for manually interacting with the experiment VMs, there is an alternative approach by using the :ref:`helper_ssh` command.
This command has the same requirements as the :ref:`helper_scp` (i.e. the experiment must be running the :ref:`control_network_mc` and VMs need to be running an SSH server).
Additionally, like the :ref:`helper_scp` command, all standard `ssh <https://linux.die.net/man/1/ssh>`_ options will work.
See the :ref:`helper_ssh` documentation for more details.
