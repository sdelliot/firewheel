from google.protobuf.json_format import MessageToDict


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
