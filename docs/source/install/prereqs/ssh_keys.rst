.. _install-ssh-config:

Configuring SSH
===================

FIREWHEEL needs the ability to SSH throughout a compute cluster without having to input passwords.
Specifically, this is a requirement of the FIREWHEEL CLI because it needs to be able to run commands on compute machines.
This is done via SSH keys at the user level.
For this document, we assume that there is a user ``fw`` on all machines within the cluster.

Create an SSH Key
-----------------

The first things that the ``fw`` user needs is an SSH key.
This can be accomplished with the ``ssh-keygen`` command.
Be sure to **not** set a password for this key to enable password-less SSH.

.. code-block:: bash

    ssh-keygen
    Generating public/private rsa key pair.
    ...

The location and name of the key is configurable based off the answers to the prompts.

Reference
^^^^^^^^^
*  https://www.ssh.com/academy/ssh/keygen#creating-an-ssh-key-pair-for-user-authentication

Configuring Password-less ``SSH``
---------------------------------

As mentioned above, the ``fw`` user needs to be able to SSH throughout the cluster without a password.
The ``ssh-copy-id`` command will add this public key across the cluster to enable password-less SSH.

.. code-block:: bash

    ssh-copy-id -i <public key> compute1
    ...


The command above configures password-less SSH to the ``compute1`` node.
This command needs to be run for all machines within this ``FIREWHEEL`` instance.

.. note::
    If using the :ref:`cluster-control-node` as a :ref:`cluster-compute-nodes`, be sure to also allow the authorized key on ``localhost`` and/or the systems hostname.

Reference
^^^^^^^^^
*  https://www.ssh.com/academy/ssh/keygen#copying-the-public-key-to-the-server

SSH Environment Variables
-------------------------
When the CLI executes a remote command, it uses a non-interactive shell.
These shells behave differently than interactive shells.
While the details of these differences are beyond the scope of this document, they notably do not use the ``~/.bashrc`` file.
If you require additional environment variables, the recommended setup is to use ``~/.ssh/environment`` (not enabled in ``sshd`` by default).
