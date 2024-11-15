.. _optimizing_disk_size:

Optimizing Disk Image Size
==========================

Many operating systems will use gratuitous amounts of disk space when there is plenty available.
Unfortunately, disks have be stored and moved around by ``FIREWHEEL``.
Therefore, it is in our best interest to have the smallest possible disk size for VMs.
Just a quick clarification here.
``FIREWHEEL`` boots VMs with copy-on-write disks so the base images are only ever changed manually by a user.
When we say that we want the smallest possible disk size we mean that we want the installed disk to be as compact as possible.
We want the VM to have lots of available hard drive space when it is running, but we don't want the disk image to be artificially inflated while it is sitting in the ``git`` repository.

The way that this can be accomplished is to install the operating system on a fairly small hard drive (thus avoiding a sparsely populated disk).
We then fill the hard drive with by creating a large file (i.e. size of the free space on the disk) that only contains zeros.
We then delete the file of zeros.
We can use ``qemu-img convert`` to deduplicate the zeros that were just created.
We then use ``qemu-img resize`` to expand the size of the disk.
Finally, we expand the VM's file system to take advantage of the newly increased disk size.

.. _note:

    This is simply an optimization to keep disks small and management slightly easier.
    This is purely optional and is not required by ``FIREWHEEL`` if you would rather not bother with these steps.

We will walk through each step for both Linux and Windows VMs.

Disk Installation
*****************

We assume that the steps covered in :ref:`building_iso` have already been completed.
You should have the VM booted and open a terminal in the VM.
If you are doing this in a Windows VM, open the command prompt as an ``Administrator``.

Filling the Hard Drive with Zeros
*********************************

Writing Zeros in Linux
^^^^^^^^^^^^^^^^^^^^^^

The first step to writing zeros to a file is to determine how many to write.
The available disk space can viewed on Linux with the following command: ::

    $ df -h
    Filesystem                       Size  Used Avail Use% Mounted on
    udev                             252G     0  252G   0% /dev
    tmpfs                             51G  258M   51G   1% /run
    /dev/sda2                         10G    7G    3G  70% /
    tmpfs                            252G     0  252G   0% /dev/shm
    tmpfs                            5.0M     0  5.0M   0% /run/lock
    tmpfs                            252G     0  252G   0% /sys/fs/cgroup

Look to see where the root partition (``/``) is mounted and check the value under ``Avail`` (in this case ``3 GB``).
That is how large of a file that will need to be created.
Creating the file of zeros can be done with the following command: ::

    $ dd if=/dev/zero of=zero.txt bs=1073741824 count=4

A quick explanation of what is going on here:

* ``if``: This is the input, in our case we need zeros, so ``/dev/zero`` will give that to us.
* ``of``: The name of the file to send the output to.
* ``bs``: This is the block size. The value ``1073741824`` correspond to 1 GB of data.
* ``count``: How many blocks of size ``bs`` to write. In this case we're writing 4 blocks of 1 GB each, therefore creating a 4 GB file.

We don't need to write exactly the right amount of zeros.
We simply need to fill the rest of the disk.
Therefore, feel free to tell the ``dd`` command to write way too many zeros.
You'll see an error that says the disk has no more free space.
That is exactly what we want.
Now delete the file that we created and shut the VM down.
Quick note, tab completion doesn't work when the disk is full. ::

    $ rm zero.txt
    $ sudo poweroff

Writing Zeros in Windows
^^^^^^^^^^^^^^^^^^^^^^^^

Similar to the Linux process, we need to find how much free space is available on the Windows VM.
One thing to note is that as the VM is booting, the values below will change.
Therefore, it is a good idea to give the system a minute to find a steady state before running the following steps.
Run the following command in an ``Administrator`` command shell (i.e. right click ``cmd.exe`` and select ``Run as Administrator``): ::

    $ fsutil volume diskfree C:
    Total # of free bytes        : 24989946985
    Total # of bytes             : 24999729152
    Total # of avail free bytes  : 24989946985

The value that we care about is ``Total # of free bytes``.
We can create a new file and zero it out by continuing to use ``fsutil``: ::

    $ fsutil file createnew C:\zero.txt 24989946985
    $ fsutil file setvaliddata C:\zero.txt 24989946985
    $ fsutil file setzerodata offset=0 length=24989946985 C:\zero.txt

We used the value from the ``fsutil volume`` command to dictate the size of the file that was created.
That was followed by setting the data to be valid and then finally setting the data to all zeros.
Once this has completed, delete the file and shut the machine down: ::

    $ del C:\zero.txt
    $ shutdown /s /t 0

Compressing the Disk Image
**************************

The disk image can be compressed by using the ``qemu-img convert`` command.
Run the following command to deduplicate the zeros that were just written to disk: ::

    $ qemu-img convert -f qcow2 -O qcow2 <disk file name> <new disk file name>

If you are doing this for the image built in :ref:`building_iso` then the disk file name is ``ubuntu-18.10-server-amd64.qcow2``.
You will need to choose a new name for the output file.
You can also rename the original disk image before running the command and then make the new disk file name ``ubuntu-18.10-server-amd64.qcow2``.
That would look as follows: ::

    $ mv ubuntu-18.10-server-amd64.qcow2 ubuntu-18.10-server-amd64-dup.qcow2
    $ qemu-img convert -f qcow2 -O qcow2 ubuntu-18.10-server-dup.qcow2 \
            ubuntu-18.10-server-amd64.qcow2

Resizing the Disk Image
***********************

Now that the extra space in the disk has been deduplicated, we need to expand the size of the disk from 10 GB up to something more reasonable for use.
The ``qemu-img resize`` command allows us to add to the size of the disk: ::

    $ qemu-img resize ubuntu-18.10-server-amd64.qcow2 +40G

This will add ``40 GB`` to the size of the disk.

Expanding the VM File System
****************************

We need to allow the VM to take advantage of the extra ``40 GB`` on the disk.
This is done by expanding the size of the file system.

Expanding the File System on Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Linux does not allow a user to resize their file system while the partition is mounted.
Therefore, you need to boot into a ``Live CD`` in order to manipulate the VM's file system.
This is generally a little easier to do via a graphical interface, so let's use an ``ISO`` for ``Ubuntu Desktop``.
Download the ``ISO`` for `Ubuntu 18.04 Desktop <https://old-releases.ubuntu.com/releases/18.10/ubuntu-18.10-desktop-amd64.iso>`_.
We need to boot the VM in a very similar way to the way that it was booted in :ref:`booting_image`.
Two changes need to be made.
First, add the `-boot d` option to tell ``QEMU`` to boot from the ``CDROM`` instead of the hard drive.
Second, change the ``file`` portion of last ``-drive`` parameter to point to ``ubuntu-18.04.1-desktop-amd64.iso``.
The new command should look like this: ::

    $ sudo  /usr/bin/qemu-system-x86_64 -nographic -nodefaults --enable-kvm -name ubuntu \
    -drive file=/opt/firewheel/ubuntu-18.10-server-amd64.qcow2,if=virtio,cache=writeback \
    -vnc 0.0.0.0:0 \
    -cpu qemu64 -smp sockets=1,cores=4,threads=2 \
    -m 8092 -vga std \
    -netdev tap,ifname=installer,id=hostnet0,script=no,downscript=no \
    -device virtio-net-pci,netdev=hostnet0,id=net0,mac=00:00:00:ff:ff:01 \
    -device piix3-usb-uhci -device usb-tablet -device piix3-usb-uhci \
    -chardev socket,id=qga0,server,nowait,path=/tmp/ga.sock \
    -device virtio-serial \
    -device virtserialport,chardev=qga0,name=org.qemu.guest_agent.0 \
    -drive file=/opt/firewheel/ubuntu-18.04.1-desktop-amd64.iso,index=2,media=cdrom \
    -boot d

Once the VM boots, choose to ``Try Ubuntu``.
You should then get put on a desktop screen.
If you click the square of dots at the bottom left corner of the screen then you'll get a search bar.
Search for ``disks`` and hit ``enter``.
You should see the disk image that you created with four partitions.
The first is where the operating system is installed.
The second and the third partitions have to do with creating a ``swap`` space.
The last partition should show up as free space and is the size that we extended the disk image by with ``qemu-img resize``.
In order to extend the first partition you first have to delete the second and third partitions.
We will add them back at the end.
Click the partition that says ``Swap Partition`` and then click the minus sign just under the lower left corner of the box.
Then do the same for the partition that says ``Extended Partition``.
With those gone you can click that partition that says ``Filesystem``.
Click the gear button that is next to the minus button.
A menu should appear.
Select the option to ``Resize``.
You should then get a box asking you for parameters for the resizing operation.
Next to ``Free Space Following`` enter  ``5 GB`` and then select the ``Resize`` button at the top left corner of the window.
This should leave ``5 GB`` of free space at the end of the hard drive.
Select the free space and then select the plus sign.
Select ``Next`` on the ``Create Partition`` page.
Select the ``Type`` to be ``other`` and then click ``Next``.
Select the type of partition to be ``linux-swap``.
Then create the partition.
Once that is done the VM can be shut down and the image can be packaged up following the instructions in :ref:`xz_image`.

Expanding the File System on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The file system on Windows machines can be extended while the machine is running and therefore there is no need for a ``Live CD`` here.
Boot the VM the same way that was done in :ref:`booting_image`.
In this case, there is no need for a ``CDROM``, but it won't hurt if it is left as part of the command.
Do **not** include the ``-boot d`` parameter that we used above.
From an ``Administrator`` command shell (i.e. ``cmd.exe``) run: ::

    $ diskmgmt.msc

You will see a window appear that has the various disks available to the VM.
Right click ``C:`` and select ``Extend Volume``.
The default settings should extend the file system to fill the newly available space on disk.
Shut down the VM and compress it using the command outlined in :ref:`xz_image`.
