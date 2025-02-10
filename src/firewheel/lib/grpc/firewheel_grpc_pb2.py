# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: firewheel/lib/grpc/firewheel_grpc.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'firewheel/lib/grpc/firewheel_grpc.proto\x12\x0e\x66irewheel_grpc\x1a\x1fgoogle/protobuf/timestamp.proto\"\x10\n\x0eGetInfoRequest\"N\n\x0fGetInfoResponse\x12\x0f\n\x07version\x18\x01 \x01(\t\x12\x0e\n\x06uptime\x18\x02 \x01(\x02\x12\x1a\n\x12\x65xperiment_running\x18\x03 \x01(\x08\"\x1e\n\x1c\x44\x65stroyAllVMMappingsResponse\"\x1a\n\x18\x44\x65stroyVMMappingResponse\",\n\x1eGetExperimentLaunchTimeRequest\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\"S\n\x14\x45xperimentLaunchTime\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\x12/\n\x0blaunch_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"+\n\x1dGetExperimentStartTimeRequest\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\"Q\n\x13\x45xperimentStartTime\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\x12.\n\nstart_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"2\n$InitializeExperimentStartTimeRequest\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\"\'\n%InitializeExperimentStartTimeResponse\"z\n\tVMMapping\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\x12\x13\n\x0bserver_uuid\x18\x02 \x01(\t\x12\x13\n\x0bserver_name\x18\x03 \x01(\t\x12\x12\n\ncontrol_ip\x18\x04 \x01(\t\x12\r\n\x05state\x18\x05 \x01(\t\x12\x14\n\x0c\x63urrent_time\x18\x06 \x01(\t\"<\n\x1f\x43ountVMMappingsNotReadyResponse\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\x12\r\n\x05\x63ount\x18\x02 \x01(\r\",\n\x1e\x43ountVMMappingsNotReadyRequest\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\"<\n\x15ListVMMappingsRequest\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\x12\x17\n\x0fjson_match_dict\x18\x02 \x01(\t\")\n\x1b\x44\x65stroyAllVMMappingsRequest\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\"0\n\rVMMappingUUID\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\x12\x13\n\x0bserver_uuid\x18\x02 \x01(\t\"O\n\x16SetVMTimeByUUIDRequest\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\x12\x13\n\x0bserver_uuid\x18\x02 \x01(\t\x12\x14\n\x0c\x63urrent_time\x18\x03 \x01(\t\"I\n\x17SetVMStateByUUIDRequest\x12\n\n\x02\x64\x62\x18\x01 \x01(\t\x12\x13\n\x0bserver_uuid\x18\x02 \x01(\t\x12\r\n\x05state\x18\x03 \x01(\t2\x98\x0b\n\tFirewheel\x12L\n\x07GetInfo\x12\x1e.firewheel_grpc.GetInfoRequest\x1a\x1f.firewheel_grpc.GetInfoResponse\"\x00\x12P\n\x12GetVMMappingByUUID\x12\x1d.firewheel_grpc.VMMappingUUID\x1a\x19.firewheel_grpc.VMMapping\"\x00\x12\x63\n\x16\x44\x65stroyVMMappingByUUID\x12\x1d.firewheel_grpc.VMMappingUUID\x1a(.firewheel_grpc.DestroyVMMappingResponse\"\x00\x12V\n\x0fSetVMTimeByUUID\x12&.firewheel_grpc.SetVMTimeByUUIDRequest\x1a\x19.firewheel_grpc.VMMapping\"\x00\x12X\n\x10SetVMStateByUUID\x12\'.firewheel_grpc.SetVMStateByUUIDRequest\x1a\x19.firewheel_grpc.VMMapping\"\x00\x12\x46\n\x0cSetVMMapping\x12\x19.firewheel_grpc.VMMapping\x1a\x19.firewheel_grpc.VMMapping\"\x00\x12V\n\x0eListVMMappings\x12%.firewheel_grpc.ListVMMappingsRequest\x1a\x19.firewheel_grpc.VMMapping\"\x00\x30\x01\x12|\n\x17\x43ountVMMappingsNotReady\x12..firewheel_grpc.CountVMMappingsNotReadyRequest\x1a/.firewheel_grpc.CountVMMappingsNotReadyResponse\"\x00\x12s\n\x14\x44\x65stroyAllVMMappings\x12+.firewheel_grpc.DestroyAllVMMappingsRequest\x1a,.firewheel_grpc.DestroyAllVMMappingsResponse\"\x00\x12n\n\x16GetExperimentStartTime\x12-.firewheel_grpc.GetExperimentStartTimeRequest\x1a#.firewheel_grpc.ExperimentStartTime\"\x00\x12\x64\n\x16SetExperimentStartTime\x12#.firewheel_grpc.ExperimentStartTime\x1a#.firewheel_grpc.ExperimentStartTime\"\x00\x12q\n\x17GetExperimentLaunchTime\x12..firewheel_grpc.GetExperimentLaunchTimeRequest\x1a$.firewheel_grpc.ExperimentLaunchTime\"\x00\x12g\n\x17SetExperimentLaunchTime\x12$.firewheel_grpc.ExperimentLaunchTime\x1a$.firewheel_grpc.ExperimentLaunchTime\"\x00\x12\x8e\x01\n\x1dInitializeExperimentStartTime\x12\x34.firewheel_grpc.InitializeExperimentStartTimeRequest\x1a\x35.firewheel_grpc.InitializeExperimentStartTimeResponse\"\x00\x42\'\n\x0e\x66irewheel_grpcB\x0e\x46irewheelProtoP\x01\xa2\x02\x02\x66wb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'firewheel.lib.grpc.firewheel_grpc_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\016firewheel_grpcB\016FirewheelProtoP\001\242\002\002fw'
  _globals['_GETINFOREQUEST']._serialized_start=92
  _globals['_GETINFOREQUEST']._serialized_end=108
  _globals['_GETINFORESPONSE']._serialized_start=110
  _globals['_GETINFORESPONSE']._serialized_end=188
  _globals['_DESTROYALLVMMAPPINGSRESPONSE']._serialized_start=190
  _globals['_DESTROYALLVMMAPPINGSRESPONSE']._serialized_end=220
  _globals['_DESTROYVMMAPPINGRESPONSE']._serialized_start=222
  _globals['_DESTROYVMMAPPINGRESPONSE']._serialized_end=248
  _globals['_GETEXPERIMENTLAUNCHTIMEREQUEST']._serialized_start=250
  _globals['_GETEXPERIMENTLAUNCHTIMEREQUEST']._serialized_end=294
  _globals['_EXPERIMENTLAUNCHTIME']._serialized_start=296
  _globals['_EXPERIMENTLAUNCHTIME']._serialized_end=379
  _globals['_GETEXPERIMENTSTARTTIMEREQUEST']._serialized_start=381
  _globals['_GETEXPERIMENTSTARTTIMEREQUEST']._serialized_end=424
  _globals['_EXPERIMENTSTARTTIME']._serialized_start=426
  _globals['_EXPERIMENTSTARTTIME']._serialized_end=507
  _globals['_INITIALIZEEXPERIMENTSTARTTIMEREQUEST']._serialized_start=509
  _globals['_INITIALIZEEXPERIMENTSTARTTIMEREQUEST']._serialized_end=559
  _globals['_INITIALIZEEXPERIMENTSTARTTIMERESPONSE']._serialized_start=561
  _globals['_INITIALIZEEXPERIMENTSTARTTIMERESPONSE']._serialized_end=600
  _globals['_VMMAPPING']._serialized_start=602
  _globals['_VMMAPPING']._serialized_end=724
  _globals['_COUNTVMMAPPINGSNOTREADYRESPONSE']._serialized_start=726
  _globals['_COUNTVMMAPPINGSNOTREADYRESPONSE']._serialized_end=786
  _globals['_COUNTVMMAPPINGSNOTREADYREQUEST']._serialized_start=788
  _globals['_COUNTVMMAPPINGSNOTREADYREQUEST']._serialized_end=832
  _globals['_LISTVMMAPPINGSREQUEST']._serialized_start=834
  _globals['_LISTVMMAPPINGSREQUEST']._serialized_end=894
  _globals['_DESTROYALLVMMAPPINGSREQUEST']._serialized_start=896
  _globals['_DESTROYALLVMMAPPINGSREQUEST']._serialized_end=937
  _globals['_VMMAPPINGUUID']._serialized_start=939
  _globals['_VMMAPPINGUUID']._serialized_end=987
  _globals['_SETVMTIMEBYUUIDREQUEST']._serialized_start=989
  _globals['_SETVMTIMEBYUUIDREQUEST']._serialized_end=1068
  _globals['_SETVMSTATEBYUUIDREQUEST']._serialized_start=1070
  _globals['_SETVMSTATEBYUUIDREQUEST']._serialized_end=1143
  _globals['_FIREWHEEL']._serialized_start=1146
  _globals['_FIREWHEEL']._serialized_end=2578
# @@protoc_insertion_point(module_scope)
