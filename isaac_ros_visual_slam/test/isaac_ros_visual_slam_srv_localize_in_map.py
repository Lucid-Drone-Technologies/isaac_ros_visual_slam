# SPDX-FileCopyrightText: NVIDIA CORPORATION & AFFILIATES
# Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import sys

from isaac_ros_test import IsaacROSBaseTest
from isaac_ros_visual_slam_interfaces.srv import LocalizeInMap
import pytest
import rclpy

sys.path.append(os.path.dirname(__file__))
from helpers import run_cuvslam_from_bag, wait_for_odometry_message  # noqa: I100 E402

_TEST_CASE_NAMESPACE = '/visual_slam_test_srv_localize_in_map'


@pytest.mark.rostest
def generate_test_description():
    bag_path = pathlib.Path(__file__).parent / 'test_cases/rosbags/r2b_galileo'
    return run_cuvslam_from_bag(_TEST_CASE_NAMESPACE, bag_path)


class IsaacRosVisualSlamServiceTest(IsaacROSBaseTest):
    """This test checks the functionality of the `visual_slam/localize_in_map` service."""

    def test_localize_in_map_service(self):
        self.assertTrue(wait_for_odometry_message(self.node, _TEST_CASE_NAMESPACE))

        service_client = self.node.create_client(
            LocalizeInMap,
            f'{_TEST_CASE_NAMESPACE}/visual_slam/localize_in_map',
        )
        self.assertTrue(service_client.wait_for_service(timeout_sec=20))

        map_path = pathlib.Path(__file__).parent / 'test_cases/rosbags/r2b_galileo/cuvslam_map'
        request = LocalizeInMap.Request()
        request.map_folder_path = str(map_path)
        request.pose_hint.position.x = 0.0
        request.pose_hint.position.y = 0.0
        request.pose_hint.position.z = 0.0
        request.pose_hint.orientation.w = 1.0
        request.pose_hint.orientation.x = 0.0
        request.pose_hint.orientation.y = 0.0
        request.pose_hint.orientation.z = 0.0

        response_future = service_client.call_async(request)
        rclpy.spin_until_future_complete(self.node, response_future)
        response = response_future.result()
        self.assertTrue(response.success)