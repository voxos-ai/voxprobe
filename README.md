# VoxProbe

VoxProbe is a tool for automated testing and evaluation of Voice AI agents.

## Installation

```
pip install .
```

## Usage

As a package:

```python
from voxprobe import VoxProbe

voxprobe = VoxProbe()
# Use VoxProbe methods here
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

