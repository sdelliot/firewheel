from google.protobuf.json_format import MessageToDict

# Metadata key used for the optional shared-token gRPC authentication.
# This is NOT the actual token, just the name of the token metadata field
GRPC_TOKEN_METADATA_KEY = "firewheel-grpc-token"  # noqa: S105


def msg_to_dict(msg):
    """
    Parses a protobuf message into a python dictionary.
    Replaces the literal string 'None' with the python NoneType.

    Args:
        msg (google.protobuf.message.Message): The message to convert.

    Returns:
        dict: Dictionary representation of protobuf message.
    """
    msg_dict = MessageToDict(
        msg, preserving_proto_field_name=True, always_print_fields_with_no_presence=True
    )
    for key, value in msg_dict.items():
        if value == "None":
            msg_dict[key] = None
    return msg_dict
