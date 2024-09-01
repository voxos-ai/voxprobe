CONVERSATION_GRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "states": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["id", "name"]
            }
        },
        "transitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from_state": {"type": "string"},
                    "to_state": {"type": "string"},
                    "condition": {"type": "string"}
                },
                "required": ["from_state", "to_state"]
            }
        },
        "start_state": {"type": "string"},
        "end_states": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["states", "transitions", "start_state", "end_states"]
}