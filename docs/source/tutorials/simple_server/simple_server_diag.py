from diagrams import Edge, Diagram
from diagrams.generic.os import Ubuntu
from diagrams.aws.analytics import Analytics
from diagrams.generic.network import Switch
from diagrams.alibabacloud.web import Domain

with Diagram("Simple Server Topology", show=True, direction="TB"):
    server = Domain("Server")
    switch = Switch()
    client = Ubuntu("Client")

    server >> Edge() << switch >> Edge() << client

with Diagram("Simple Server Complex Topology", show=True, direction="TB"):
    server = Domain("Server")
    switch = Switch()

    server >> Edge() << switch

    # Build the clients
    for i in range(10):
        client = Ubuntu(f"Client-{i}")
        client >> Edge(label="Random Delay") << switch

with Diagram("Simple Server Tap Topology", show=True, direction="TB"):
    server = Domain("Server")
    switch = Switch()
    analysis = Analytics("Collector")
    edge = Edge()
    server >> Edge() << switch
    server >> Edge(label="Tap") >> analysis

    # Build the clients
    for i in range(1):
        client = Ubuntu(f"Client-{i}")
        client >> Edge(label="Random Delay") << switch
