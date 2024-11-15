.. _elk-setup:

*************************
DEPRECATED Setting Up ELK
*************************

.. error::
    This module has been deprecated in favor of using Jupyter notebooks. The remainder of this module is dedicated to installing ELK and ingesting VM resource logs. However, this will be removed in a future release.

In this module, you will install Elasticsearch and Kibana and learn how to ingest experiment data into them.
While FIREWHEEL does not officially support/automate the installation of these tools, they will be useful for your experiment analysis.

The following script, which assumes unobstructed access to the Internet, will install Elasticsearch and Kibana on Ubuntu.

.. note::
    Please update the ``ELK_VERSION`` to use the latest supported version found here: https://www.elastic.co/downloads/elasticsearch/!!!


.. code-block:: bash
   :caption: ``setup_es.sh``

    #!/bin/bash

    ELK_VERSION="8.13.4"

    pushd /tmp

    # Install elasticsearch
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-$ELK_VERSION-amd64.deb
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-$ELK_VERSION-amd64.deb.sha512
    shasum -a 512 -c elasticsearch-$ELK_VERSION-amd64.deb.sha512
    sudo dpkg -i elasticsearch-$ELK_VERSION-amd64.deb

    # Install kibana
    wget https://artifacts.elastic.co/downloads/kibana/kibana-$ELK_VERSION-amd64.deb
    wget https://artifacts.elastic.co/downloads/kibana/kibana-$ELK_VERSION-amd64.deb.sha512
    shasum -a 512 kibana-$ELK_VERSION-amd64.deb.sha512
    sudo dpkg -i kibana-$ELK_VERSION-amd64.deb

    # Start the system services
    sudo systemctl daemon-reload
    sudo systemctl enable elasticsearch.service
    sudo systemctl enable kibana.service

    sudo systemctl start elasticsearch
    sudo systemctl start kibana

    # Storing the HTTP Certificates and the basic authentication password
    # NOTE: This is NOT production safe code!
    sudo cp /etc/elasticsearch/certs/http_ca.crt .
    sudo /usr/share/elasticsearch/bin/elasticsearch-reset-password -a -b -u elastic -s > es_pass.txt

    popd

.. note::
   If there are issues running the script and installing Elasticsearch or Kibana, be sure to check your network settings for any potential issues (e.g., proxies, firewalls, etc.).

*********************************
Ingesting Data into Elasticsearch
*********************************

Once Elasticsearch is installed, we can use the `elasticsearch-py <https://elasticsearch-py.readthedocs.io/en/latest/>`_, the official Python package, to help ingest our data.
First install this package into our virtual environment.

.. code-block:: bash

    $ source /opt/firewheel/fwpy/bin/activate
    $ python -m pip install elasticsearch

Then we can use the following script to ingest our data:

.. code-block:: python
    :caption: ``ingest_json_file.py``

    #!/usr/bin/env python3

    import sys
    import json
    from elasticsearch import Elasticsearch, helpers, exceptions

    def generate_data(paths):
        """
        Reads all VM Resource Logs and properly formats them to
        yield a single document. This function is passed into the bulk()
        helper to create many documents in sequence.
        """
        for fn in paths:
            with open(fn) as f:
                for line in f:
                    formatted = json.loads(line.rstrip())
                    timestamp = formatted['timestamp']
                    formatted['timestamp'] = timestamp.replace(' ', 'T')
                    yield formatted

    paths = sys.argv[1:]
    index = 'vm_resource_logs'

    es_pass = ""
    with open("/tmp/es_pass.txt") as f:
        es_pass = f.read()

    es_client = Elasticsearch(
        'https://localhost:9200',
        ca_certs="/tmp/http_ca.crt",
        basic_auth=("elastic", es_pass)
    )

    try:
        es_resp = helpers.bulk(client=es_client, actions=generate_data(paths), index=index)
    except exceptions.ConnectionError as e:
        print("ERROR: sending data to Elasticsearch, it may not be up yet")
        raise

Save the script as ``ingest_json_file.py``.
Now we can call ``ingest_json_file.py`` with our JSON logs as the argument.

.. code-block:: bash

    $ python ingest_json_file.py /scratch/vm_resource_logs/*.json

.. note::
   If your default shell does not expand the ``*`` you will need to modify ``ingest_json_file.py`` to ingest the desired files.

Depending on how your cluster is configured, Kibana will likely be running on http://localhost:5601.
If you had to port-forward your miniweb dashboard, you will need to do the same for Kibana (e.g. ``ssh -Llocalhost:9001:localhost:9001 -Llocalhost:5601:localhost:5601 <node>``.

Once you open Kibana, you can create a new visualization to explore the data.
We defer to external tutorials/resources for information on how to use Kibana.
