from diagrams import Edge, Cluster, Diagram
from diagrams.generic.os import Ubuntu
from diagrams.aws.general import TraditionalServer, GenericOfficeBuilding
from diagrams.aws.network import InternetGateway
from diagrams.generic.place import Datacenter
from diagrams.onprem.network import Vyos
from diagrams.generic.network import Switch, Firewall

with Diagram("ACME Topology", show=True, direction="TB"):
    gateway = InternetGateway("Gateway")
    firewall = Firewall("Firewall")

    b1 = GenericOfficeBuilding("Building 1")
    with Cluster("Building 1"):
        b1_workers = [
            Ubuntu("Host 3"),
            Ubuntu("Host 2"),
            Ubuntu("Host 1"),
        ]

    b2 = GenericOfficeBuilding("Building 2")
    with Cluster("Building 2"):
        b2_workers = [
            Ubuntu("Host 6"),
            Ubuntu("Host 5"),
            Ubuntu("Host 4"),
        ]

    with Cluster("Data Center"):
        dc_servers = [
            TraditionalServer("Server 3"),
            TraditionalServer("Server 2"),
            TraditionalServer("Server 1"),
        ]

    gateway >> firewall

    firewall >> b1 >> b1_workers

    b2 >> b2_workers
    b2 >> Datacenter("Data Center") >> dc_servers

    firewall >> b2


with Diagram("Network Topology", show=True, direction="LR"):
    inet = Switch("Internet")
    gw_fw_switch = Switch()
    gateway = Vyos("gateway.acme.com")
    firewall = Vyos("firewall.acme.com")
    internal_switch = Switch()

    b1 = Vyos("building1.acme.com")
    b1_switch = Switch()
    with Cluster("Building 1"):
        b1_workers = [
            Ubuntu("building_1-host_3.acme.net"),
            Ubuntu("building_1-host_2.acme.net"),
            Ubuntu("building_1-host_1.acme.net"),
        ]

    b2 = Vyos("building2.acme.com")
    b2_switch = Switch()
    with Cluster("Building 2"):
        b2_workers = [
            Ubuntu("building_2-host_6.acme.net"),
            Ubuntu("building_2-host_5.acme.net"),
            Ubuntu("building_2-host_4.acme.net"),
        ]

    dc = Vyos("datacenter.acme.com")
    dc_switch = Switch()
    with Cluster("Data Center"):
        dc_servers = [
            Ubuntu("datacenter-3.acme.net"),
            Ubuntu("datacenter-2.acme.net"),
            Ubuntu("datacenter-1.acme.net"),
        ]

    inet >> Edge() << gateway >> Edge() << gw_fw_switch >> Edge() << firewall
    firewall >> Edge() << internal_switch

    internal_switch >> Edge() << b1 >> Edge() << b1_switch
    internal_switch >> Edge() << b2 >> Edge() << b2_switch

    b1_switch >> Edge() << b1_workers
    b2_switch >> Edge() << b2_workers
    b2_switch >> Edge() << dc

    dc >> Edge() << dc_switch >> Edge() << dc_servers
