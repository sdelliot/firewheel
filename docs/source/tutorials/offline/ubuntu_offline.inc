.. _offline-ubuntu:

Ubuntu Debian Packages
======================
To install a collection of debian packages in a FIREWHEEL experiment, users can simply call the :py:meth:`install_debs <linux.ubuntu.UbuntuHost.install_debs>` method (assuming that their VM has been decorated as a :py:class:`linux.ubuntu.UbuntuHost`).
However, how users need to first collect all the necessary packages.
First, we recommend starting an Internet-accessible VM using the exact same image that will be used in FIREWHEEL (see :ref:`vm_builder` for an example).
Once the VM is started, you can follow the following steps:

#. Clear out ``/var/cache/apt/archives`` of any remaining ``.deb`` files.
   This ensures that you only save off files that were not previously available to the VM.

   .. code-block:: bash

      $ sudo rm -f /var/cache/apt/archives/*.deb

   That directory should now look similar to:

   .. image:: ./images/ubuntu_offline_1.png
      :alt: Clearing the apt archives.

#. Install the necessary packages using ``apt-get install``.

   .. warning::

      This method will **not** work if the packages are installed with ``apt install``!
      Additionally, similar methods like using ``apt-get download`` or ``apt-get install --download-only`` will **only** download the specific package, not any dependencies.

   .. code-block:: bash

      $ # In this example, we will install curl
      $ sudo apt-get install curl

   .. image:: ./images/ubuntu_offline_2.png
      :alt: Installing a needed package (e.g. :command:`curl`).

#. The installed ``.deb`` files and all installed dependencies/updates will now be located in ``/var/cache/apt/archives``.

   .. image:: ./images/ubuntu_offline_3.png
      :alt: Locating the installed packages.

#. Create a directory in the home folder and copy all ``.deb`` files into that directory.

   .. code-block:: bash

      $ mkdir curl_debs
      $ sudo cp /var/cache/apt/archives/*.deb curl_debs/

   .. image:: ./images/ubuntu_offline_4.png
      :alt: Locating the installed packages.

#. Compress the folder and copy it off of the VM.

   .. code-block:: bash

      $ tar -czvf curl_debs.tgz curl_debs

   .. image:: ./images/ubuntu_offline_5.png
      :alt: Locating the installed packages.

Now you are ready to use the generated tarball as a VM resource.
That is, you can move it to your Model Components directory and add it to the MANIFEST file.
Then, in your Plugin or Model Component Objects file, you can call the :py:meth:`install_debs <linux.ubuntu.UbuntuHost.install_debs>` method.

   .. code-block:: python

      # Example of using the newly created VM Resource
      vm = Vertex(self.g, "example-vm")
      vm.decorate(Ubuntu1604Server)
      vm.install_debs(-5, "curl_debs.tgz")


Alternative Approaches:
-----------------------

* Using `apt-offline <https://manpages.ubuntu.com/manpages/bionic/man8/apt-offline.8.html>`_.
