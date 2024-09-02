# VoxProbe

VoxProbe is a tool for automated testing and evaluation of Voice AI agents.

## Installation

```
pip install -e . 
```

## Usage

As a package:

```python
from voxprobe import VoxProbe

from voxprobe.datasets import Dataset
from voxprobe.agents import BolnaAgent
from voxprobe.testing.telephony_tester.twilio_tester import TwilioTester
bolna_agent = BolnaAgent(api_key = "")
bolna_agent.pull()

dataset = Dataset(agent_prompt)

twilio_tester = TwilioTester(bolna_agent, dataset, 
                             twilio_account_sid="",
                             twilio_auth_token="",
                             twilio_incoming_number="")

# Run the tester
twilio_tester.run()
```

As a CLI tool:

```
voxprobe [command] [arguments]
```

Available commands:
- import: Import an agent
- generate: Generate seed data
- test: Run automated tests
- ingest: Ingest recordings
- evaluate: Evaluate conversations

## Features

- Import agents from various platforms (Vocode, Retell, Vapi, Bolna)
- Generate seed data for testing
- Automate testing using generated datasets
- Ingest call recordings and create golden datasets
- Create and use evaluation datasets
- Evaluate actual conversations

## Development

To start developing, navigate to the respective directories and implement the TODO items in each file.

