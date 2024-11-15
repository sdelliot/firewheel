.. _mc-install-tutorial:

#########################################
Creating a Model Component INSTALL Script
#########################################

In this tutorial we will demonstrate how to create and use a :ref:`mc_install`.
We will be referencing the :ref:`BIOS Tutorial <bios-tutorial>`.
In that tutorial, users needed to download an open source BIOS to use with the experiment.
In that case, `SeaBIOS <https://www.seabios.org/SeaBIOS>`_ is licensed under `GNU LGPLv3 <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_ which may differ from the desired license of the given Model Component.
Therefore, it's advantageous to have new MC users download their own copy of the software rather than to package/re-host the image with the Model Component [#]_.
This strategy of downloading the BIOS for each new user also helps save space/clutter within a MCs git repository.

To enable the automated downloading of various files, Model Components can use an :ref:`INSTALL file <mc_install>`.
This a template of this file is generated when using the :ref:`helper_mc_generate` Helper.

Let's start by creating a new Model Component (if you already completed :ref:`BIOS Tutorial <bios-tutorial>`, you may have done this step).

We will create our new Model Component using the :ref:`helper_mc_generate` command:

.. code-block:: bash

    $ firewheel mc generate
    (name) ModelComponent name : tutorials.bios
    (attribute_depends) (space-separated-strings) Graph Attribute(s) depended on by the new ModelComponent []: graph
    (attribute_provides) (space-separated-strings) Graph Attribute(s) provided by the new ModelComponent []: topology
    (attribute_precedes) (space-separated-strings) Graph Attribute(s) preceded by the new ModelComponent []:
    (model_component_depends) (space-separated-strings) ModelComponent(s) required by name []: base_objects linux.ubuntu1604
    (model_component_precedes) (space-separated-strings) ModelComponent(s) that will be preceded by name []:
    (plugin) File for a plugin []: plugin.py
    (model_component_objects) File for Model Component Objects []:
    (location) Location for the new ModelComponent : /opt/firewheel/model_components/bios
    (vm_resources) (space-separated-strings) File(s) to be used as a vm_resource []:
    (image) File to be used as a VM disk []: images/bios.bin.tar.gz
    (arch) Architecture for specified image []: x86_64

This command will automatically create an INSTALL file located in ``/opt/firewheel/model_components/bios/INSTALL``.

This template has several pre-built functions which can be used by MC creators to help future users download/install packages.

.. seealso::

    The full template can be found in :ref:`mc_install`.

For this tutorial, we need to add the ability for users to download the BIOS software and prepare it for usage.
Additionally, we need to help users ensure that they have downloaded the file correctly, so we will provide a checksum as well.
Open the file and towards the bottom, there will be a commented out section where an example of downloading/checksumming a file is shown.

.. code-block:: bash

    # Be sure to use SHA-256 hashes for the checksums (e.g. shasum -a 256 <file>)
    # file1=("url1" "e0287e6339a4e77232a32725bacc7846216a1638faba62618a524a6613823df5" "file1")
    # file2=("url2" "53669e1ee7d8666f24f82cb4eb561352a228b1136a956386cd315c9291e59d59" "file2")
    # files=(file1 file2)
    # wget_and_checksum "${files[@]}"
    # echo "Downloaded and checksummed all files!"

Update this section to include creating the ``images`` directory and then add the correct URL:

.. code-block:: bash

    mkdir -p images
    pushd images
    file1=("https://www.seabios.org/downloads/bios.bin-1.14.0.gz" "c774e04aa95c6e1bf16799290ec59b106b3d1898653763a9922ec2d39ae1930c" "bios.bin-1.14.0.gz")
    files=(file1)
    wget_and_checksum "${files[@]}"
    echo "Downloaded and checksummed all files!"

After downloading and verifying, we will rename the file because QEMU requires the BIOS to have the ``.bin`` extension.
Additionally, we will use tar+gzip which can be automatically decompressed by FIREWHEEL.

These commands can be added following the checksum code:

.. code-block:: bash

    echo "Checksums are valid!"
    # Decompress and make it more generic
    gunzip bios.bin-1.14.0.gz
    mv bios.bin-1.14.0 bios.bin
    tar -czvf bios.bin.tar.gz bios.bin
    rm bios.bin
    popd

Finally, we want to make sure to clean up any data if an error occurs.
There is a ``cleanup`` function within the INSTALL file that helps with this:

.. code-block:: bash

    function cleanup() {
        echo "Cleaning up tutorials.bios install"
        # TODO: Cleanup any downloaded files
        # rm -rf file.tar
        rm -rf $INSTALL_FLAG
        exit 1
    }

That should be updated to look like:

.. code-block:: bash

    function cleanup() {
        echo "Cleaning up tutorials.bios install"
        rm -rf bios.bin*
        rm -rf $INSTALL_FLAG
        exit 1
    }

Now that the INSTALL file is complete, we can try it out by installing it as a FIREWHEEL repository.

.. note::

    If you already followed the :ref:`BIOS Tutorial <bios-tutorial>`, you will need to first *uninstall* the repository by running ``firewheel repository uninstall /opt/firewheel/model_components/bios``.

The :ref:`helper_repository_install` Helper has a ``-s`` option which will enable users to execute MC INSTALL scripts for all MCs within the repository.
Run the following (note that some output has been trimmed in this example):

.. code-block:: bash

    $ firewheel repository install -s /opt/firewheel/model_components/bios
    Running any Model Component install scripts. This could be a DANGEROUS operation!!! Ensure that you completely trust the Model Component creator before continuing!
    Do you want to execute /opt/firewheel/model_components/bios/INSTALL [y/n/v/vc/q]: y
    Starting to install tutorials.bios!
    ...
    Installed tutorials.bios!
    All model components were installed or skipped!
    Repository successfully installed!

.. note::

    For offline users or those whom may have issues reaching the Internet due to various network security devices (e.g. proxies, firewalls, etc.) various ``wget`` options (in a ``~/.wgetrc``) may be necessary.

The script will notify you if any errors occurred so that you can fix them.
Now, other users will be able to easily use this MC and have the same behavior as the original developer.

.. [#] Please consult a lawyer prior to determining the best strategy for distributing your Model Component.
