# Copyright 2023 MLRun Authors
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
import mlrun.common.runtimes


class ClientLocalRuntime(mlrun.common.runtimes.AbstractFindMeAName):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def verify_base_image(runtime):
        pass

    @staticmethod
    def save(runtime):
        pass

    @staticmethod
    def run(runtime):
        pass

    @staticmethod
    def _enrich_and_validate(runtime):
        pass

    def _run_local(self, runtime):
        pass
