# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: server_services.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'server_services.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15server_services.proto\x12\x0fserver_services\"6\n\x13SendFileRequestBody\x12\x0c\n\x04\x66ile\x18\x01 \x01(\x0c\x12\x11\n\tfile_name\x18\x02 \x01(\t\"8\n\x14SendFileResponseBody\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"8\n\x15SendFileChunksRequest\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\x12\x11\n\tfile_name\x18\x02 \x01(\t\":\n\x16SendFileChunksResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2\xcf\x01\n\x0fSendFileService\x12W\n\x08SendFile\x12$.server_services.SendFileRequestBody\x1a%.server_services.SendFileResponseBody\x12\x63\n\x0eSendFileChunks\x12&.server_services.SendFileChunksRequest\x1a\'.server_services.SendFileChunksResponse(\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'server_services_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SENDFILEREQUESTBODY']._serialized_start=42
  _globals['_SENDFILEREQUESTBODY']._serialized_end=96
  _globals['_SENDFILERESPONSEBODY']._serialized_start=98
  _globals['_SENDFILERESPONSEBODY']._serialized_end=154
  _globals['_SENDFILECHUNKSREQUEST']._serialized_start=156
  _globals['_SENDFILECHUNKSREQUEST']._serialized_end=212
  _globals['_SENDFILECHUNKSRESPONSE']._serialized_start=214
  _globals['_SENDFILECHUNKSRESPONSE']._serialized_end=272
  _globals['_SENDFILESERVICE']._serialized_start=275
  _globals['_SENDFILESERVICE']._serialized_end=482
# @@protoc_insertion_point(module_scope)
