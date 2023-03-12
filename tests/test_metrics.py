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
from metrics_gen.deployment_generator import deployment_generator
from metrics_gen.metrics_generator import Generator_df
import pandas as pd
import yaml


def get_deployment(configuration: dict) -> pd.DataFrame:
    dep_gen = deployment_generator()
    deployment = dep_gen.generate_deployment(configuration=configuration)
    return deployment


class TestMetrics:
    configuration: dict = yaml.safe_load(
        open(
            "./tests/test_configuration.yaml",
            "r",
        )
    )
    metrics_configuration: dict = configuration.get("metrics", {})
    deployment: pd.DataFrame = get_deployment(configuration)

    def test_metric_as_dict(self):
        met_gen = Generator_df(self.configuration, user_hierarchy=self.deployment)
        generator = met_gen.generate(as_df=False)
        assert (generator, "No generated data was created")

    def test_metric_as_df(self):
        met_gen = Generator_df(self.configuration, user_hierarchy=self.deployment)
        generator = met_gen.generate(as_df=True)
        assert (generator, "No generated data was created")
