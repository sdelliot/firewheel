.. _developer-using-git:

#############
Using Git LFS
#############

For storing large binary files in Git, we use `Git Large File Storage (LFS) <https://git-lfs.com/>`__.
This document should help you get started with LFS and use it in the context of FIREWHEEL.

**********************
When should I use LFS?
**********************
You should use LFS whenever you have files that meet any of the following criteria:

* Binary in nature -- tarballs, images, executables, etc.
* When the size of the file is greater than a few KBs

Here is a good article on when/why to use LFS: https://testdouble.com/insights/why-use-git-large-file-storage

**************
Setting up LFS
**************
In order to use git LFS, you must do the following:

.. lfs-inclusion-marker

Installing LFS
==============
Before installing Git LFS it is highly recommended to install Git version 2.17 or later.
This version of Git has vastly improved the speed of cloning an LFS repository.
You can install the latest version of Git by following the instructions listed `here <https://git-scm.com/download/linux>`__.

To install `git-lfs <https://git-lfs.com/>`__ you can follow the instructions `here <https://github.com/git-lfs/git-lfs/wiki/Installation>`__.

Setting up ``.gitconfig``
=========================
Once Git LFS is installed you need to initialize your ``.gitconfig`` file.
You can do this by running the command: ``git lfs install``.
This may complain that you are not in a Git repository but that is okay.
You need to verify that your ``~/.gitconfig`` includes the following lines:

.. code-block:: bash

    [filter "lfs"]
        clean = git-lfs clean -- %f
        smudge = git-lfs smudge -- %f
        process = git-lfs filter-process
        required = true

.. lfs-stop-marker

*****************
Retrieving files:
*****************
If you have cloned a repository which has only downloaded certain files due to the
``lfs.fetchinclude`` parameter in ``.lfsconfig`` then you can download additional files by using:

.. code-block:: bash

    $ git lfs pull -I <file>

You can provide a relative file path or a wild card * to this command as well.

*****************
Adding a new file
*****************

Tracking files
==============
If you are adding a new file type, you first need to track the file. You can
track individual files as well as classes of files using wild cards.

Example of tracking files:

.. code-block:: bash

    $ git lfs track *.tar *.zip # Track all files with a tar or zip extension
    $ git lfs track myfile.big  # Track an indvidual file

**Note:** You **MUST** run this from the root of the Git repository.

Adding files
============
Once the file is tracked you can add the LFS file like any other file If you have
tracked a new file or set of files, you will also need to add the ``.gitattributes``
file which was either newly created or modified

.. code-block:: bash

    $ git add myfile.big
    $ git add .gitattributes

Confirm LFS will be used
========================
Before committing/pushing the files, you should verify that LFS will be used.
You can use the ``git lfs status`` command.

.. code-block:: bash

    $ git lfs status
    On branch master
    Git LFS objects to be pushed to origin/master:


    Git LFS objects to be committed:

        .gitattributes (Git: f7c4224 -> Git: c91cb31)
        myfile.big (LFS: 219633d)

    Git LFS objects not staged for commit:

Notice, the parentheses next to each file. Object tracked using LFS will state
that, whereas, non-lfs files will show they are tracked by Git.

Once you verify that the file will be committed as an LFS file, you can ``git commit``
and ``git push`` as normal.

************************
Using `.lfsconfig` Files
************************
The ``.lfsconfig`` is a file that can be placed in the root of a Git repository
that can modify the default LFS behavior for the repository. One of the more useful
parameters is the ability to include/exclude specific files.

To learn more about ``.lfsconfig`` files see: https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-config.adoc

Including/Excluding certain files:
==================================

* ``lfs.fetchinclude`` -- When fetching, only download objects which match any entry on this
  comma-separated list of paths/filenames. Wildcard matching is as per
  `gitignore <https://git-scm.com/docs/gitignore>`__. See `git-lfs-fetch(1) <https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-fetch.adoc>`__ for examples.

* ``lfs.fetchexclude`` -- When fetching, do not download objects which match any item on this
  comma-separated list of paths/filenames. Wildcard matching is as per
  `gitignore <https://git-scm.com/docs/gitignore>`__. See `git-lfs-fetch(1) <https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-fetch.adoc>`__ for examples.
