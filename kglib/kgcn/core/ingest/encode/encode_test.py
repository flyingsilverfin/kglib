#
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.
#
import os
import subprocess as sp
import unittest

import grakn.client
import numpy as np
import tensorflow as tf

import kglib.kgcn.core.ingest.encode.encode as encode
from kglib.kgcn.test.base import GraknServer

TEST_KEYSPACE = "test_schema"
TEST_URI = "localhost:48555"


class TestEncode(unittest.TestCase):

    def test_encode(self):
        client = grakn.client.GraknClient(uri=TEST_URI)
        session = client.session(keyspace=TEST_KEYSPACE)
        tx = session.transaction().write()
        encoder = encode.Encoder(tx)

        placeholders = [
            {'role_type': tf.placeholder(dtype=tf.string, shape=(None, 1)),
             'role_direction': tf.placeholder(dtype=tf.int64, shape=(None, 1)),
             'neighbour_type': tf.placeholder(dtype=tf.string, shape=(None, 1)),
             'neighbour_data_type': tf.placeholder(dtype=tf.string, shape=(None, 1)),
             'neighbour_value_long': tf.placeholder(dtype=tf.int64, shape=(None, 1)),
             'neighbour_value_double': tf.placeholder(dtype=tf.float32, shape=(None, 1)),
             'neighbour_value_boolean': tf.placeholder(dtype=tf.int64, shape=(None, 1)),
             'neighbour_value_date': tf.placeholder(dtype=tf.int64, shape=(None, 1)),
             'neighbour_value_string': tf.placeholder(dtype=tf.string, shape=(None, 1))
             }
        ]

        encoded_output = encoder(placeholders)

        example_arrays = {
            'role_type': np.full((4, 1), fill_value='employee', dtype=np.dtype('U50')),
            'role_direction': np.full((4, 1), fill_value=0, dtype=np.int),
            'neighbour_type': np.full((4, 1), fill_value='person', dtype=np.dtype('U50')),
            'neighbour_data_type': np.full((4, 1), fill_value='', dtype=np.dtype('U10')),
            'neighbour_value_long': np.full((4, 1), fill_value=0, dtype=np.int),
            'neighbour_value_double': np.full((4, 1), fill_value=0.0, dtype=np.float),
            'neighbour_value_boolean': np.full((4, 1), fill_value=0, dtype=np.int),
            'neighbour_value_date': np.full((4, 1), fill_value=0, dtype=np.int),
            'neighbour_value_string': np.full((4, 1), fill_value='', dtype=np.dtype('U50'))
        }

        feed_dict = {placeholder: example_arrays[placeholder_name] for placeholder_name, placeholder in
                     placeholders[0].items()}

        init_global = tf.global_variables_initializer()
        init_tables = tf.tables_initializer()

        tf_session = tf.Session()
        tf_session.run(init_global)
        tf_session.run(init_tables)

        tf_session.run(encoded_output, feed_dict=feed_dict)


if __name__ == "__main__":

    with GraknServer() as gs:

        sp.check_call([
            'grakn', 'console', '-k', TEST_KEYSPACE, '-f',
            os.getenv("TEST_SRCDIR") + '/kglib/kglib/kgcn/test_data/schema.gql'
        ], cwd=gs.grakn_binary_location)

        unittest.main()
