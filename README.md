# metrics-gen

dummy metrics generator

## Getting Started
Metrics generator is built upon three main components:

- **Deployment**: The indexes of the table, for example:
  - symbol in stock market.
  - (data_center, device_id) for devices in data centers
- **Static Data**: Static data regarding the deployment, for example:
  - model_number for a device
  - score for a model
- **Metrics**: Continuous metrics to generate about the deployment, for example:
  - cpu_utilization of a device
  - price of a stock

The first step in setting up the generator is creating a deployment.  Then using the deployment, you can generate static data or continuous stream of metrics.

### Create a deployment from configuration
To create a deployment from configuration you need to provide a **yaml** file containing the following:

```yaml
deployment:
    <level_name>:
      faker: <faker_type>
      num_items: <num_items in the level>
```

Where `level_name` will be the name of the index, `faker_type` is the name of the [faker generator](https://github.com/joke2k/faker) and `num_items` is how many keys to create for this index.  
Each provided level will create another `num_items` instances for each entry in it's previous levels.

**Example**: Given the following configuration yaml file:

```yaml
deployment:
    device:
      faker: msisdn
      num_items: 2
    core:
      faker: msisdn
      num_items: 2
```

and running the following command:
```python
from metrics_gen.deployment_generator import deployment_generator

dep_gen = deployment_generator()
deployment = dep_gen.generate_deployment(configuration=configuration)
```

Will generate the following example deployment:

| | device      |     core |
|- |- |-|
| 0 | 4120271911677 | 6950611701382 |
| 1 | 4120271911677 | 2255426557707 |
| 2 | 4120271911677 | 7717168891372 |
| 3 | 2260158002886 | 3213635322383 |
| 4 | 2260158002886 | 4007792940086 |
| 5 | 2260158002886 | 3720953132595 |

**Notice** that each extra level, multiplies the number of items created by `num_item`, thus we got 2 * 3 = 6 items created.

### Create Static Data
To create a static data generator you need to supply a deployment dataframe and a configuration yaml.

The static data generator knows how to generator from two kinds of feature configurations: **range** and **choice** which should be specified in the yaml.

```yaml
static:
    <feature_name>:
        kind: range
        min_range: <min_feature_range>, defaults to 0
        max_range: <max_feature_range>
        as_integer: <int or float>, defaults to False
    <feature_name>:
        kind: choice
        choices: <list of possible choices>
```

Each provided feature will generate a new feature column in the generated dataframe.

Example: Given the following yaml:

```yaml
static:
    models: 
      kind: range
      min_range: 10
      max_range: 15
      as_integer: True
    country: 
      kind: choice
      choices: [A, B, C, D, E, F, G]
```

And the previous deployment:

```python
from metrics_gen.static_data_generator import Static_data_generator


static_data_generator = Static_data_generator(
    deployment, static_configuration
)

generated_df = static_data_generator.generate_static_data()
```

Will generate the following dataframe:


|  | device | core | models | country |
|-- |------- |----- |------- |-----
| 0 | 4120271911677 | 6950611701382  |    13   |    A |
| 1 | 4120271911677 | 2255426557707  |    14   |    C |
| 2 | 4120271911677 | 7717168891372  |    14   |    G |
| 3 | 2260158002886 | 3213635322383  |    14   |    G |
| 4 | 2260158002886 | 4007792940086  |    11   |    G |
| 5 |  2260158002886 | 3720953132595  |    14   |    D |

### Create Continuous Metrics

To create a continuous metrics stream you need to provide a deployment dataframe and metrics creation configuration yaml.

```yaml
errors:
    rate_in_ticks: < ~ticks between errors>
    length_in_ticks: < ~length of error mode>
timestamps:
    interval: <time between samples in seconds>
    stochastic_interval: <create random intervals (around interval)>
metrics:
  <metric name>:
    accuracy: <decimals to produce>
    distribution: normal
    distribution_params:
        mu: <mean>
        noise: <noise>
        sigma: <std>
    is_threshold_below: <True to produce max when in error mode, False for min>
    past_based_value: <True to add the latest metric to the last result (like in daily stock market), False to replace normally)
    produce_max: <True for candles-like presentation>
    produce_min: <True for candles-like presentation>
    validation:
        distribution: # per-sample validation
            max: <max value for individual sample>
            min: <min value for individual sample>
            validate: <True to activate validation>
      metric: # metric level validations
        max: <max value for overall-metric sample (only applicable to past-based-values)>
        min: <min value for overall-metric sample (only applicable to past-based-values)>
        validate: <True to activate validation>
```

Each configured feature will generate additional metric for your deployment.

Example: Given the following yaml

```yaml
errors: {length_in_ticks: 10, rate_in_ticks: 5}
timestamps: {interval: 5s, stochastic_interval: true}
metrics:
  cpu_utilization:
    accuracy: 2
    distribution: normal
    distribution_params: {mu: 70, noise: 0, sigma: 10}
    is_threshold_below: true
    past_based_value: false
    produce_max: false
    produce_min: false
    validation:
      distribution: {max: 1, min: -1, validate: false}
      metric: {max: 100, min: 0, validate: true}
  throughput:
    accuracy: 2
    distribution: normal
    distribution_params: {mu: 250, noise: 0, sigma: 20}
    is_threshold_below: false
    past_based_value: false
    produce_max: false
    produce_min: false
    validation:
      distribution: {max: 1, min: -1, validate: false}
      metric: {max: 300, min: 0, validate: true}
```

And the previous deployment:

```python
from metrics_gen.metrics_generator import Generator_df

metrics_generator = Generator_df(metrics_configuration, user_hierarchy=deployment)
generator = metrics_generator.generate(as_df=True)

df = next(generator)
```

Will generate the following dataframe:

| timestamp                  	| core          	| device        	| cpu_utilization    	| cpu_utilization_is_error 	| throughput         	| throughput_is_error 	| is_error 	|
|----------------------------	|---------------	|---------------	|--------------------	|--------------------------	|--------------------	|---------------------	|----------	|
| 2022-01-31 19:20:21.007087 	| 2113309831673 	| 4469221325973 	| 100.0              	| True                     	| 0.0                	| True                	| True     	|
| 2022-01-31 19:20:21.007087 	| 2115933686087 	| 4469221325973 	| 100.0              	| True                     	| 235.0679405785135  	| False               	| False    	|
| 2022-01-31 19:20:21.007087 	| 0175482390171 	| 4469221325973 	| 70.26657388732976  	| False                    	| 208.34378630077305 	| False               	| False    	|
| 2022-01-31 19:20:21.007087 	| 1626403145660 	| 4038890878426 	| 59.932750968399404 	| False                    	| 217.4335871243806  	| False               	| False    	|
| 2022-01-31 19:20:21.007087 	| 7247058922310 	| 4038890878426 	| 83.98361382584898  	| False                    	| 265.3476318369042  	| False               	| False    	|
| 2022-01-31 19:20:21.007087 	| 7030239128061 	| 4038890878426 	| 100.0              	| False                    	| 225.16604191632058 	| False               	| False    	|

To generate new samples all we need to do is call `next(generator)` and a new sample will be generated.

