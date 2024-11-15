from diagrams import Edge, Diagram
from diagrams.generic.os import Ubuntu
from diagrams.onprem.network import Vyos

with Diagram(
    name="The router tree topology with 3 branches",
    filename="router_tree",
    show=True,
    direction="TB",
):
    root_host = Ubuntu("host.root.net")
    root_ospf = Vyos("ospf.root.net")
    root_bgp = Vyos("bgp.root.net")

    (
        root_host
        >> Edge(color="darkgreen")
        << root_ospf
        >> Edge(color="darkgreen")
        << root_bgp
    )

    # Build the tree structure
    for i in range(3):
        bgp = Vyos(f"bgp.leaf-{i}.net")
        root_bgp >> Edge(color="darkgreen") << bgp

        ospf = Vyos(f"ospf.leaf-{i}.net")
        bgp >> Edge(color="darkgreen") << ospf
        host = Ubuntu(f"host.leaf-{i}.net")
        ospf >> Edge(color="darkgreen") << host
