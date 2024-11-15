from typing import Union as _Union
from typing import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional

from google.protobuf import message as _message
from google.protobuf import descriptor as _descriptor
from google.protobuf import timestamp_pb2 as _timestamp_pb2

DESCRIPTOR: _descriptor.FileDescriptor

class CountVMMappingsNotReadyRequest(_message.Message):
    __slots__ = ["db"]
    DB_FIELD_NUMBER: _ClassVar[int]
    db: str
    def __init__(self, db: _Optional[str] = ...) -> None: ...

class CountVMMappingsNotReadyResponse(_message.Message):
    __slots__ = ["count", "db"]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    DB_FIELD_NUMBER: _ClassVar[int]
    count: int
    db: str
    def __init__(
        self, db: _Optional[str] = ..., count: _Optional[int] = ...
    ) -> None: ...

class DestroyAllVMMappingsRequest(_message.Message):
    __slots__ = ["db"]
    DB_FIELD_NUMBER: _ClassVar[int]
    db: str
    def __init__(self, db: _Optional[str] = ...) -> None: ...

class DestroyAllVMMappingsResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class DestroyVMMappingResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ExperimentLaunchTime(_message.Message):
    __slots__ = ["db", "launch_time"]
    DB_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_TIME_FIELD_NUMBER: _ClassVar[int]
    db: str
    launch_time: _timestamp_pb2.Timestamp
    def __init__(
        self,
        db: _Optional[str] = ...,
        launch_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class ExperimentStartTime(_message.Message):
    __slots__ = ["db", "start_time"]
    DB_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    db: str
    start_time: _timestamp_pb2.Timestamp
    def __init__(
        self,
        db: _Optional[str] = ...,
        start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class GetExperimentLaunchTimeRequest(_message.Message):
    __slots__ = ["db"]
    DB_FIELD_NUMBER: _ClassVar[int]
    db: str
    def __init__(self, db: _Optional[str] = ...) -> None: ...

class GetExperimentStartTimeRequest(_message.Message):
    __slots__ = ["db"]
    DB_FIELD_NUMBER: _ClassVar[int]
    db: str
    def __init__(self, db: _Optional[str] = ...) -> None: ...

class GetInfoRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetInfoResponse(_message.Message):
    __slots__ = ["experiment_running", "uptime", "version"]
    EXPERIMENT_RUNNING_FIELD_NUMBER: _ClassVar[int]
    UPTIME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    experiment_running: bool
    uptime: float
    version: str
    def __init__(
        self,
        version: _Optional[str] = ...,
        uptime: _Optional[float] = ...,
        experiment_running: bool = ...,
    ) -> None: ...

class InitializeExperimentStartTimeRequest(_message.Message):
    __slots__ = ["db"]
    DB_FIELD_NUMBER: _ClassVar[int]
    db: str
    def __init__(self, db: _Optional[str] = ...) -> None: ...

class InitializeExperimentStartTimeResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ListRepositoriesRequest(_message.Message):
    __slots__ = ["db"]
    DB_FIELD_NUMBER: _ClassVar[int]
    db: str
    def __init__(self, db: _Optional[str] = ...) -> None: ...

class ListVMMappingsRequest(_message.Message):
    __slots__ = ["db", "json_match_dict"]
    DB_FIELD_NUMBER: _ClassVar[int]
    JSON_MATCH_DICT_FIELD_NUMBER: _ClassVar[int]
    db: str
    json_match_dict: str
    def __init__(
        self, db: _Optional[str] = ..., json_match_dict: _Optional[str] = ...
    ) -> None: ...

class RemoveAllRepositoriesRequest(_message.Message):
    __slots__ = ["db"]
    DB_FIELD_NUMBER: _ClassVar[int]
    db: str
    def __init__(self, db: _Optional[str] = ...) -> None: ...

class RemoveAllRepositoriesResponse(_message.Message):
    __slots__ = ["removed_count"]
    REMOVED_COUNT_FIELD_NUMBER: _ClassVar[int]
    removed_count: int
    def __init__(self, removed_count: _Optional[int] = ...) -> None: ...

class RemoveRepositoryResponse(_message.Message):
    __slots__ = ["removed_count"]
    REMOVED_COUNT_FIELD_NUMBER: _ClassVar[int]
    removed_count: int
    def __init__(self, removed_count: _Optional[int] = ...) -> None: ...

class Repository(_message.Message):
    __slots__ = ["db", "path"]
    DB_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    db: str
    path: str
    def __init__(
        self, db: _Optional[str] = ..., path: _Optional[str] = ...
    ) -> None: ...

class SetRepositoryResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class SetVMStateByUUIDRequest(_message.Message):
    __slots__ = ["db", "server_uuid", "state"]
    DB_FIELD_NUMBER: _ClassVar[int]
    SERVER_UUID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    db: str
    server_uuid: str
    state: str
    def __init__(
        self,
        db: _Optional[str] = ...,
        server_uuid: _Optional[str] = ...,
        state: _Optional[str] = ...,
    ) -> None: ...

class SetVMTimeByUUIDRequest(_message.Message):
    __slots__ = ["current_time", "db", "server_uuid"]
    CURRENT_TIME_FIELD_NUMBER: _ClassVar[int]
    DB_FIELD_NUMBER: _ClassVar[int]
    SERVER_UUID_FIELD_NUMBER: _ClassVar[int]
    current_time: str
    db: str
    server_uuid: str
    def __init__(
        self,
        db: _Optional[str] = ...,
        server_uuid: _Optional[str] = ...,
        current_time: _Optional[str] = ...,
    ) -> None: ...

class VMMapping(_message.Message):
    __slots__ = [
        "control_ip",
        "current_time",
        "db",
        "server_name",
        "server_uuid",
        "state",
    ]
    CONTROL_IP_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TIME_FIELD_NUMBER: _ClassVar[int]
    DB_FIELD_NUMBER: _ClassVar[int]
    SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVER_UUID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    control_ip: str
    current_time: str
    db: str
    server_name: str
    server_uuid: str
    state: str
    def __init__(
        self,
        db: _Optional[str] = ...,
        server_uuid: _Optional[str] = ...,
        server_name: _Optional[str] = ...,
        control_ip: _Optional[str] = ...,
        state: _Optional[str] = ...,
        current_time: _Optional[str] = ...,
    ) -> None: ...

class VMMappingUUID(_message.Message):
    __slots__ = ["db", "server_uuid"]
    DB_FIELD_NUMBER: _ClassVar[int]
    SERVER_UUID_FIELD_NUMBER: _ClassVar[int]
    db: str
    server_uuid: str
    def __init__(
        self, db: _Optional[str] = ..., server_uuid: _Optional[str] = ...
    ) -> None: ...
