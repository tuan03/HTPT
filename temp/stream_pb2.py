# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: stream.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'stream.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cstream.proto\"\x07\n\x05\x45mpty\"\x1f\n\x0c\x44\x61taResponse\x12\x0f\n\x07message\x18\x01 \x01(\t26\n\rStreamService\x12%\n\nStreamData\x12\x06.Empty\x1a\r.DataResponse0\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'stream_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_EMPTY']._serialized_start=16
  _globals['_EMPTY']._serialized_end=23
  _globals['_DATARESPONSE']._serialized_start=25
  _globals['_DATARESPONSE']._serialized_end=56
  _globals['_STREAMSERVICE']._serialized_start=58
  _globals['_STREAMSERVICE']._serialized_end=112
# @@protoc_insertion_point(module_scope)