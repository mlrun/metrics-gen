# Copyright 2022 Iguazio
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
#
from metrics_gen.static_data_generator import Static_data_generator
from metrics_gen.deployment_generator import deployment_generator
import pandas as pd
import yaml


def get_deployment(configuration: dict) -> pd.DataFrame:
    dep_gen = deployment_generator()
    deployment = dep_gen.generate_deployment(configuration=configuration)
    return deployment


class TestStaticData:
    metrics_configuration: dict = yaml.safe_load(
        open(
            "./tests/test_configuration.yaml",
            "r",
        )
    )
    static_configuration: dict = metrics_configuration.get("static", {})
    deployment: pd.DataFrame = get_deployment(metrics_configuration)

    def test_create_generator_with_full_configuration(self):
        static_data_generator = Static_data_generator(
            self.deployment, self.metrics_configuration
        )
        assert (
            static_data_generator,
            "Static data generator failed to be created from a full file configuration",
        )

    def test_create_generator_with_static_configuration(self):
        static_data_generator = Static_data_generator(
            self.deployment, self.static_configuration
        )
        assert (
            static_data_generator,
            "Static data generator failed to be created from static configuration",
        )

    def test_static_data_created(self):
        static_data_generator = Static_data_generator(
            self.deployment, self.static_configuration
        )

        generated_df = static_data_generator.generate_static_data()
        assert (
            not generated_df.equals(self.deployment),
            "No static data was generated, returned original deployment DF",
        )
