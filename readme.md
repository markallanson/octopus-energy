# Octopus Energy Python API Client Library
A Client library for accessing the Octopus Energy APIs

***Warning: The API is currently undergoing active development and should be considered unstable,
even volatile until it reaches version 1.0.0***

[![PyPI version](https://badge.fury.io/py/octopus-energy.svg)](https://badge.fury.io/py/octopus-energy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/octopus-energy)

[![Build Status](https://travis-ci.com/markallanson/octopus-energy.svg?branch=main)](https://travis-ci.com/markallanson/octopus-energy)
[![Coverage Status](https://coveralls.io/repos/github/markallanson/octopus-energy/badge.svg?branch=main)](https://coveralls.io/github/markallanson/octopus-energy?branch=main)

## Installation
`octopus-energy` can be installed from PyPI using pip:

```shell
pip install octopus-energy
```

## Code
The code is available in the [octopus-energy repository on GitHub][github]

## Features

* Get energy consumption from SMETS1 and SMETS2 electricity and gas meters.

## Quickstart
You can obtain your API token and meter information from the [Octopus Energy Developer 
Dashboard][octo dashboard].

```python
from octopus_energy import OctopusEnergyClient, MeterType

api_token="sk_live_your-token"
mprn = "your-mprn"
serial_number = "your-meter-serial-number"

client = OctopusEnergyClient(api_token)
consumption = await client.get_gas_consumption_v1(mprn, serial_number, MeterType.SMETS1_GAS)
```

[github]: https://github.com/markallanson/octopus-energy
[octo dashboard]: https://octopus.energy/dashboard/developer/
