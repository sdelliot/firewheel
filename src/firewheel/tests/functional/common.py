import time
from subprocess import call

from firewheel.config import config
from firewheel.lib.grpc.firewheel_grpc_client import FirewheelGrpcClient

# pylint: disable=invalid-name
launch_mc = "minimega.launch"


def firewheel_restart():
    """
    Restarts firewheel.

    Returns:
        int: The return code of `firewheel restart`.
    """
    # Clear any running experiment
    # No user input can be passed to this command
    cmd = ["firewheel", "restart"]
    ret = call(cmd)  # nosec
    return ret


def initialize_grpc_client():
    """
    Initialize the grpc client.

    Returns:
        FirewheelGrpcClient: The initialized grpc client.
    """
    grpc_client = FirewheelGrpcClient(
        hostname=config["grpc"]["hostname"],
        port=config["grpc"]["port"],
        db=config["grpc"]["db"],
    )
    return grpc_client


def get_experiment_launch(grpc_client):
    """
    Gets the experiment launch time.

    Args:
        grpc_client (FirewheelGrpcClient): The grpc client to query with.

    Returns:
        datetime.datetime: The datetime that the experiment was launched.
    """
    launch_time = grpc_client.get_experiment_launch_time()
    return launch_time


def get_experiment_start(grpc_client):
    """
    Gets the experiment launch time.

    Args:
        grpc_client (FirewheelGrpcClient): The grpc client to query with.

    Returns:
        datetime.datetime: The datetime that the experiment was started.
    """
    start_time = grpc_client.get_experiment_start_time()
    return start_time


def count_vms_not_configured(grpc_client):
    """
    Returns the count of vms that are not configured.

    Args:
        grpc_client (FirewheelGrpcClient): The grpc client to query with.

    Returns:
        int: Count of the not configured VMs.
    """
    res = grpc_client.count_vm_mappings_not_ready()
    return res["count"]


def poll_not_configured(grpc_client, expected_count=0, timeout=1000, period=2):
    """
    Polls the number of not configured VMs until the expected count is
    returned or timeout.

    Args:
        grpc_client (FirewheelGrpcClient): The grpc client to query with.
        expected_count (int): The expected count of not configured VMs.
        timeout (int): The number of seconds to wait before returning early.
        period (int): The number of seconds before polls.

    Returns:
        int: Count of the not configured VMs.
    """
    attempts = timeout // period
    not_configured_count = count_vms_not_configured(grpc_client)
    for attempt in range(attempts):
        if attempt % 10 == 0:
            print(f"attempt #{attempt}, not_configured_count={not_configured_count}")
        if not_configured_count == expected_count:
            break

        time.sleep(period)
        not_configured_count = count_vms_not_configured(grpc_client)
    return not_configured_count


def poll_start_time(grpc_client, timeout=1000, period=2):
    """
    Polls the number of not configured VMs until the start time is set
    or timeout.

    Args:
        grpc_client (FirewheelGrpcClient): The grpc client to query with.
        timeout (int): The number of seconds to wait before returning early.
        period (int): The number of seconds before polls.

    Returns:
        datetime.datetime: The datetime that the experiment was launched.
    """
    attempts = timeout // period
    cur_experiment_start_time = get_experiment_start(grpc_client)
    for attempt in range(attempts):
        print(
            f"attempt #{attempt}, cur_experiment_start_time={cur_experiment_start_time}"
        )
        if cur_experiment_start_time is not None:
            break

        time.sleep(period)
        cur_experiment_start_time = get_experiment_start(grpc_client)
    return cur_experiment_start_time
