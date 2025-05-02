.. _mc_install:

############################
Model Component INSTALL file
############################

Some Model Components may require additional Python packages to be installed within FIREWHEEL's virtual environment or for data to be downloaded.
In this case, the Model Component can have an ``INSTALL`` file, which can be either a valid `Ansible Playbook <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html>`_ (recommend method) or any executable script (as denoted by a `shebang <https://en.wikipedia.org/wiki/Shebang_(Unix)>`_ line).

When a repository is installed via the :ref:`helper_repository_install` Helper, users have the option to can automatically run each MCs INSTALL script using the ``-s`` flag (see :ref:`helper_repository_install` for more details).

*************************
INSTALL File Requirements
*************************

Regardless of whether the INSTALL file is an Ansible Playbook or an executable, FIREWHEEL expects the following:

1. Upon successful installation, a new file is created in the model component directory with the following format: ``.<MC Name>.installed``. For example, if the model component name is ``dns.dns_objects`` than the new file would be ``.dns.dns_objects.installed``.
2. After execution, all non-packaged dependencies for the model component should be met.

*****************
Design Principles
*****************

In addition to the requirements above, we recommend that the following principles are adhered to when creating a new INSTALL file.

1. `Idempotence <https://en.wikipedia.org/wiki/Idempotence>`_ - The file should be capable of running multiple times without causing issues. This is a core tenant of Ansible and a strong motivator why Ansible Playbooks are the preferred INSTALL file method.
2. **Reproducibility** - It is critical that users will download the exact same data that was originally intended by the Model Component creators.
   If the data/packages differ, than there is a strong possibility that the experimental outcomes will differ and could produce unintended consequences.
   Therefore, we strongly recommend that MC creators link to exact versions of software to download, rather than an automatically updating link.
   For example, if the MC was supposed to install a GitLab runner:

   .. code-block:: bash

        # This will automatically get the latest URL, this is BAD
        wget https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64

        # This will get a specific version, this is GOOD!
        wget https://s3.amazonaws.com/gitlab-runner-downloads/v11.4.2/binaries/gitlab-runner-linux-386

3. **Integrity** - A checksum for all downloaded files is strongly recommend both to facilitate reproducibility and to increase the security of the experiment.
4. **Offline Accessible** - Many experiments are conducted on infrastructure that lacks Internet access. Therefore, we recommend that INSTALL files allow users to achieve the same end result using cached files. While we do not expect users to support all methods for retrieving these cached files, we suggest designing the INSTALL file to ensure that the presence of these files does not lead to errors.
5. **Cleanup** - INSTALL files should include only the essential dependencies and should remove any irrelevant data that may have been generated during intermediate steps.
6. **Readability** - Users will need to execute these potentially unknown actions, the INSTALL script should be well documented and readable to the average user. Readability is desired over brevity.


.. _mc_install_ansible:

*********************
Ansible INSTALL Files
*********************

While INSTALL files should not have an extension, if INSTALL contains valid YAML, is a list, and has the "hosts" key in each list entry, then FIREWHEEL will attempt to use Ansible to execute the file.
We strongly recommend using ``localhost`` as the "hosts" value.
We also recommend that users define an ``install_flag`` variable and a ``cached_files`` variable (if needed).

Below is beginning of an example Ansible "play":

.. code-block:: yaml

    ---
    - name: Download DNS Data files
      hosts: localhost
      become: yes
      vars:
        install_flag: "{{ playbook_dir }}/.dns.dns_objects.installed"
        cached_files:
          - source: "firewheel_repo_dns/dns_objects/bind9_xenial_debs.tgz"
            destination: "vm_resources/bind9_xenial_debs.tgz"

When designing the tasks, recall that it is possible that the existing ``cached_files`` to become available prior to playbook execution.

************
Cached Files
************

FIREWHEEL supports collecting pre-computed blobs from various resources to enable offline experiment access.
To enable retrieving files from a cache, users should set the ``ansible.cache_type`` to ``git`` or ``s3`` depending on if the files are cached in a git repository or in an Amazon S3 data store.
This is an optional feature and the default value for ``ansible.cache_type`` is ``online``.
See :ref:`firewheel_configuration` for additional information.

Path Convention
===============
The source of the file within the cache should always be: ``<package name>/path/to/file``.
In the case of git, note that the ``<package name>`` is **NOT** the repository name.
For example, if we cloned the cache for ``dns.dns_objects`` the structure would look like::

    firewheel_repo_dns -- Cloned repository
    └── firewheel_repo_dns
        └── dns_objects
            └── bind9_xenial_debs.tgz

URL Cache
=========
If users have access to any file server (HTTP/HTTPS/FTP), they can specify the ``ansible.cache_type`` key as ``url`` in the :ref:`firewheel_configuration`.
Additional configuration options under the ``ansible`` key are also necessary.
If these values are not provided, but ``ansible.cache_type`` is ``url``, the user will be prompted for the information.

- ``url`` - The URL of the server hosting the cached files.
- ``url_cache_path`` - The path to the file's base directory from the server. For example: ``http://example.com/<url_cache_path>/file.txt``.
- ``use_proxy`` - (optional) If ``false``, it will not use a proxy, even if one is defined in an environment variable on the target hosts. The default is: ``true``.
- ``validate_certs`` - (optional) If ``false``, SSL certificates will not be validated. The default is: ``true``.

If you are using an username or password token, you can specify it in the URL.
For example: ``https://user:password@server.com/url/cache/path/file.txt``

Git Cache
=========
If users have access to a git server instance, they can specify the ``ansible.cache_type`` key as ``git`` in the :ref:`firewheel_configuration`.
Additional configuration options under the ``ansible`` key are also necessary.
If these values are not provided, but ``ansible.cache_type`` is ``git``, the user will be prompted for the information.

- ``git_server`` - The URL of the git server.
- ``git_repo_path`` - The path to the repo from the server. Because this is likely to change for each model component, we recommend not setting this parameter and simply prompting the user for each path.
- ``git_branch`` - (optional) The branch name, defaults to ``main``.

If an access token is being used, the user can specify it in the ``git_server`` URL.
For example: ``https://<token>@github.com/user/repo.git``

S3 Cache
========
If users have access to an AWS S3 instance, they can specify the ``ansible.cache_type`` key as ``s3`` in the :ref:`firewheel_configuration`.
Additional configuration options under the ``ansible`` key are also necessary.
If these values are not provided, but ``ansible.cache_type`` is ``s3``, the user will be prompted for the information.

- ``s3_endpoint`` - The S3 instance URL
- ``s3_bucket`` - The name of the S3 bucket name
- ``aws_access_key_id`` - The AWS access key
- ``aws_secret_access_key`` - The AWS secret key

****************
INSTALL Template
****************

The file ``src/firewheel/control/utils/templates/INSTALL.template`` contains a template for a Bash-based INSTALL file.
When users use the :ref:`helper_mc_generate` Helper, this file is automatically added to the MC directory.
The current template is shown below.

.. literalinclude:: ../../../src/firewheel/control/utils/templates/INSTALL.template
    :language: bash
    :caption: INSTALL template
    :name: INSTALL
