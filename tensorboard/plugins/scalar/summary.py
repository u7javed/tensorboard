# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Scalar summaries and TensorFlow operations to create them.

A scalar summary stores a single floating-point value, as a rank-0 tensor.

NOTE: This module is in beta, and its API is subject to change, but the
data that it stores to disk will be supported forever.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np

from tensorboard.compat.proto import summary_pb2
from tensorboard.plugins.scalar import metadata
from tensorboard.util import tensor_util


def scalar(name, tensor, tag=None, description=None, step=None):
  """Create a scalar summary op.

  Arguments:
    name: A name for the generated summary node.
    tensor: A real numeric rank-0 `Tensor`. Must have `dtype` castable
      to `float32`.
    tag: Optional rank-0 string `Tensor` to identify this summary in
      TensorBoard.  Defaults to the generated name of this op.
    description: Optional long-form description for this summary, as a
      constant `str`. Markdown is supported. Defaults to empty.
    step: Optional `int64` monotonic step variable, which defaults
      to `tf.train.get_global_step`.

  Returns:
    A TensorFlow summary op.
  """
  # TODO(nickfelt): make tag param work
  summary_metadata = metadata.create_summary_metadata(
      display_name=None, description=description)
  with tf.name_scope(name, values=[tensor, tag, step]) as scope:
    with tf.control_dependencies([tf.assert_scalar(tensor)]):
      return tf.contrib.summary.generic(name=scope,
                                        tensor=tf.cast(tensor, tf.float32),
                                        metadata=summary_metadata,
                                        step=step)


def scalar_pb(tag, tensor, description=None):
  """Create a scalar summary_pb2.Summary protobuf.

  Arguments:
    tag: String tag for the summary.
    tensor: A rank-0 `np.array` or a compatible python number type.
    description: Optional long-form description for this summary, as a
      `str`. Markdown is supported. Defaults to empty.

  Returns:
    A `summary_pb2.Summary` protobuf object.
  """
  arr = np.array(tensor)
  if arr.shape != ():
    raise ValueError('Expected scalar shape for tensor, got shape: %s.'
                     % arr.shape)
  if arr.dtype.kind not in ('b', 'i', 'u', 'f'):  # bool, int, uint, float
    raise ValueError('Cast %s to float is not supported' % arr.dtype.name)
  tensor_proto = tensor_util.make_tensor_proto(arr.astype(np.float32))
  summary_metadata = metadata.create_summary_metadata(
      display_name=None, description=description)
  summary = summary_pb2.Summary()
  summary.value.add(tag=tag,
                    metadata=summary_metadata,
                    tensor=tensor_proto)
  return summary


def op(name,
       data,
       display_name=None,
       description=None,
       collections=None):
  """Create a legacy scalar summary op.

  Arguments:
    name: A unique name for the generated summary node.
    data: A real numeric rank-0 `Tensor`. Must have `dtype` castable
      to `float32`.
    display_name: Optional name for this summary in TensorBoard, as a
      constant `str`. Defaults to `name`.
    description: Optional long-form description for this summary, as a
      constant `str`. Markdown is supported. Defaults to empty.
    collections: Optional list of graph collections keys. The new
      summary op is added to these collections. Defaults to
      `[Graph Keys.SUMMARIES]`.

  Returns:
    A TensorFlow summary op.
  """
  if display_name is None:
    display_name = name
  summary_metadata = metadata.create_summary_metadata(
      display_name=display_name, description=description)
  with tf.name_scope(name):
    with tf.control_dependencies([tf.assert_scalar(data)]):
      return tf.summary.tensor_summary(name='scalar_summary',
                                       tensor=tf.cast(data, tf.float32),
                                       collections=collections,
                                       summary_metadata=summary_metadata)


def pb(name, data, display_name=None, description=None):
  """Create a legacy scalar summary protobuf.

  Arguments:
    name: A unique name for the generated summary, including any desired
      name scopes.
    data: A rank-0 `np.array` or array-like form (so raw `int`s and
      `float`s are fine, too).
    display_name: Optional name for this summary in TensorBoard, as a
      `str`. Defaults to `name`.
    description: Optional long-form description for this summary, as a
      `str`. Markdown is supported. Defaults to empty.

  Returns:
    A `tf.Summary` protobuf object.
  """
  data = np.array(data)
  if data.shape != ():
    raise ValueError('Expected scalar shape for data, saw shape: %s.'
                     % data.shape)
  if data.dtype.kind not in ('b', 'i', 'u', 'f'):  # bool, int, uint, float
    raise ValueError('Cast %s to float is not supported' % data.dtype.name)
  tensor = tf.compat.v1.make_tensor_proto(data.astype(np.float32))

  if display_name is None:
    display_name = name
  summary_metadata = metadata.create_summary_metadata(
      display_name=display_name, description=description)
  tf_summary_metadata = tf.SummaryMetadata.FromString(
      summary_metadata.SerializeToString())
  summary = tf.Summary()
  summary.value.add(tag='%s/scalar_summary' % name,
                    metadata=tf_summary_metadata,
                    tensor=tensor)
  return summary
