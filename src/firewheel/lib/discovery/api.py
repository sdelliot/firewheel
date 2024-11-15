import os
import time

import requests

from firewheel.config import Config
from firewheel.lib.log import Log
from firewheel.lib.minimega.api import minimegaAPI


# The proper way to spell discovery is ALWAYS lowercase.
# pylint: disable=invalid-name
class discoveryAPI:  # noqa: N801
    """
    This class implements an API to discovery.
    """

    def __init__(self, hostname=None, port=None):
        """
        Initializes the object.

        Args:
            hostname (str): discovery hostname
            port (int): discovery port number
        """

        config = Config().get_config()
        if not hostname:
            hostname = config["discovery"]["hostname"]

        if not port:
            port = config["discovery"]["port"]

        self.log = Log(name="discoveryAPI").log
        self.bind_addr = f"{hostname}:{port}"
        self.discovery_URI = f"http://{self.bind_addr}"
        self.log_file = None

    def start_discovery(self):
        """
        Start the discovery service with minimega if it is not already started.

        Returns:
            bool: True if it was started successfully, False otherwise.
        """
        config = Config().get_config()
        if self.test_connection():
            return True
        bin_path = os.path.join(config["discovery"]["install_dir"], "bin", "discovery")
        self.log_file = os.path.join(
            config["logging"]["root_dir"], config["logging"]["discovery_log"]
        )
        misc_path = os.path.join(config["discovery"]["install_dir"], "misc")
        command = [
            f"{bin_path}",
            "-level",
            f"{config['logging']['level'].lower()}",
            "-logfile",
            f"{self.log_file}",
            "-serve",
            f"{self.bind_addr}",
            "-verbose",
            "true",
            "-web",
            f"{misc_path}",
        ]
        try:
            minimega_api = minimegaAPI()
            minimega_api.mm.background(" ".join(command))
        except (RuntimeError, TimeoutError) as exp:
            self.log.exception(exp)
            return False

        # Ensure that discovery has been started
        for _attempt in range(12):
            time.sleep(5)  # Wait a few seconds to ensure it has started
            if self.test_connection():
                return True
        return False

    def test_connection(self):
        """
        Check to see if the discovery API is active.

        Returns:
            bool: True if the discovery server is up, False otherwise.
        """
        try:
            res = requests.get(f"{self.discovery_URI}/config", timeout=60)
            if res.status_code == requests.codes.ok:
                return True
            print(f"Invalid repsonse code: {res}")
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.InvalidURL:
            print(
                f"The discovery URL `{self.bind_addr}` is not valid. "
                "Please update the configuration using:\n"
                "\t``firewheel config set -s discovery.hostname <value>`` or\n"
                "\t``firewheel config set -s discovery.port <value>``"
            )
            return False
        return False

    def get_config(self, config_key=""):
        """
        Get the config value for key, config_key. If no key is provided, returns entire config.

        Args:
            config_key (str): config key.

        Returns:
            dict: Config as a dictionary.
        """
        ret = requests.get(f"{self.discovery_URI}/config/{config_key}", timeout=60)
        ret.raise_for_status()
        return ret.json()

    def set_config(self, config_key, config_value):
        """
        Set the config value for key, config_key, to config_value.

        Args:
            config_key (str): config key.
            config_value (dict): The new value for the given ``config_key``.

        Returns:
            bool: True on success.
        """
        ret = requests.post(
            f"{self.discovery_URI}/config/{config_key}", data=config_value, timeout=60
        )
        ret.raise_for_status()
        return ret.ok

    def insert_network(self):
        """
        Insert a network.

        Returns:
            dict: Dictionary representation of response. On success, this is
                  the inserted network.
        """
        ret = requests.post(f"{self.discovery_URI}/networks/", json=[{}], timeout=60)
        ret.raise_for_status()
        return ret.json()

    def get_networks(self):
        """
        Get all networks.

        Returns:
            list: A list of all networks on success.
        """
        ret = requests.get(f"{self.discovery_URI}/networks/", timeout=60)
        ret.raise_for_status()
        networks = ret.json()
        if networks is None:
            return []
        return networks

    def delete_networks(self, key="", value=""):
        """
        Delete networks. If key and value are provided, then all networks with matching
            key:value are deleted. If only value is provided, then all networks that have any
            key with a matching value are deleted.

        Args:
            key (str): network key
            value (str): network value

        Returns:
            list: List of dictionary representations of deleted networks.
        """
        if key and value:
            ret = requests.delete(
                f"{self.discovery_URI}/networks/{key}/{value}", timeout=60
            )
        else:
            ret = requests.delete(f"{self.discovery_URI}/networks/{value}", timeout=60)
        ret.raise_for_status()
        deleted_networks = ret.json()
        if deleted_networks is None:
            return []
        return deleted_networks

    def get_endpoints(self):
        """
        Get all endpoints.

        Returns:
            list: A list of all endpoints on success.
        """
        ret = requests.get(f"{self.discovery_URI}/endpoints/", timeout=60)
        ret.raise_for_status()
        endpoints = ret.json()
        if endpoints is None:
            return []
        return endpoints

    def delete_endpoints(self, key="", value=""):
        """
        Delete endpoints. If key and value are provided, then all endpoints with matching
            key:value are deleted. If only value is provided, then all endpoints that have any
            key with a matching value are deleted.

        Args:
            key (str): endpoint key
            value (str): endpoint value

        Returns:
            list: List of dictionary representations of deleted endpoints.
        """
        if key and value:
            ret = requests.delete(
                f"{self.discovery_URI}/endpoints/{key}/{value}", timeout=60
            )
        else:
            ret = requests.delete(f"{self.discovery_URI}/endpoints/{value}", timeout=60)
        ret.raise_for_status()
        deleted_endpoints = ret.json()
        if deleted_endpoints is None:
            return []
        return deleted_endpoints

    def delete_all_endpoints(self):
        """
        Deletes all endpoints.

        Returns:
            list: List of dictionary representations of deleted endpoints.
        """
        deleted_endpoints = []
        endpoints = self.get_endpoints()
        if len(endpoints) == 0:
            return deleted_endpoints
        new_deleted_endpoints = self.delete_endpoints(value="qemu")
        deleted_endpoints.extend(new_deleted_endpoints)
        endpoints = self.get_endpoints()
        if len(endpoints) == 0:
            return deleted_endpoints
        for endpoint in endpoints:
            nid = endpoint["NID"]
            deleted_endpoint = self.delete_endpoints(key="NID", value=nid)
            deleted_endpoints.extend(deleted_endpoint)
        return deleted_endpoints

    def delete_all_networks(self):
        """
        Deletes all networks.

        Returns:
            list: List of dictionary representations of deleted networks.
        """
        deleted_networks = []
        networks = self.get_networks()
        if len(networks) == 0:
            return deleted_networks
        for network in networks:
            nid = network["NID"]
            deleted_network = self.delete_networks(key="NID", value=nid)
            deleted_networks.extend(deleted_network)
        return deleted_networks

    def delete_all(self):
        """
        Deletes all endpoints and networks.

        Returns:
            bool: True on success.

        Raises:
            RuntimeError: If not all the endpoints or networks were successfully deleted.
        """
        self.delete_all_endpoints()
        endpoints = self.get_endpoints()
        if endpoints:
            raise RuntimeError("discovery endpoints not successfully deleted.")
        self.delete_all_networks()
        networks = self.get_networks()
        if networks:
            raise RuntimeError("Networks not successfully deleted from discovery")
        return True

    def insert_endpoint(self, mm_node_properties=None):
        """
        Insert endpoint with the provided properties.

        Args:
            mm_node_properties (dict): Dictionary of node properties.

        Returns:
            list: List of dictionary representations of inserted endpoints on success.
        """
        data = {"D": mm_node_properties}
        ret = requests.post(f"{self.discovery_URI}/endpoints/", json=[data], timeout=60)
        ret.raise_for_status()
        return ret.json()

    def update_endpoint(self, mm_node_properties=None):
        """
        Updates endpoint with corresponding ``mm_node_properties``.
        This matches on ``NID`` in ``mm_node_properties``.

        Args:
            mm_node_properties (dict): Dictionary of node properties.

        Returns:
            list: List of dictionary representations of inserted endpoints on success.
        """
        data = mm_node_properties
        ret = requests.put(f"{self.discovery_URI}/endpoints/", json=[data], timeout=60)
        ret.raise_for_status()
        return ret.json()

    def connect_endpoint(self, node_id, network_id):
        """
        Connect node with ``node_id`` to network with ``network_id``.

        Args:
            node_id (str): Node identifier.
            network_id (str): Network identifier.

        Returns:
            dictionary: Dictionary of updated endpoint.
        """
        req = f"{self.discovery_URI}/connect/{network_id}/{node_id}"
        ret = requests.post(req, timeout=60)
        ret.raise_for_status()
        return ret.json()
