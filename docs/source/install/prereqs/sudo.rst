.. _sudo:

Password-less ``sudo``
======================

Some system-level commands on which FIREWHEEL or one of its dependencies rely require ``root`` access to run (e.g ``qemu-system-x86_64``, ``ovs-vsctl``, etc.).
FIREWHEEL is moving towards limiting the requirement of ``root`` access for normal users, but it is a work in progress.
In the meantime, FIREWHEEL users need to be able to run commands with password-less ``sudo``.

There are multiple methods of doing so and a knowledgeable system administrator will be able to help configure this correctly for the given environment.
For ease-of-use, we provide examples for two such methods.

Example
-------

.. warning::
    Always verify with a system administrator before modifying the ``sudoers`` file as it can have detrimental consequences.

.. warning::
    It is always recommended that one use `visudo <https://linux.die.net/man/8/visudo>`_ to modify the ``sudoers`` file.

If you wanted to grant the ``fw`` user password-less ``sudo`` then you would open ``visudo``::

    $ sudo visudo

Then you would add the following line::

    fw ALL=(ALL) NOPASSWD: ALL

Alternatively, you can script this action by using the command::

    echo 'fw ALL=(ALL) NOPASSWD:ALL' | sudo EDITOR='tee -a' visudo

For more information please see the following links:

* https://www.simplified.guide/linux/enable-passwordless-sudo
* https://www.digitalocean.com/community/tutorials/how-to-edit-the-sudoers-file
* https://stackoverflow.com/a/28382838
