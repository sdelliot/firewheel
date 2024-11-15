.. _git-lfs:

*******
Git LFS
*******
Many of FIREWHEEL model component repositories contain large binary files.
Therefore, for storing these files in Git we use `Git Large File Storage (LFS) <https://git-lfs.github.com/>`__.
Generally, this only needs to be installed on your :ref:`cluster-control-node`.
For more information on using LFS please see :ref:`developer-using-git`.

.. include:: ../../developer/git-lfs.rst
   :start-after: lfs-inclusion-marker
   :end-before: lfs-stop-marker
