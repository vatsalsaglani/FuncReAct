from typing import List, Union
from pydantic import BaseModel
from enum import Enum


class Actions(Enum):
    """Actions available for the agent.
    Only SearchKB action is available
    """

    SEARCH_KB = "SearchKB"


class Action(BaseModel):
    """Schema for Action takes the name of the action
    as action_type and argument for that action as search_text
    """

    action_type: Actions
    search_text: str


class Thought(BaseModel):
    """Thought scheama contains text for the thought"""

    thought_text: str


class Observation(BaseModel):
    """Observation schema contains text for the observation being made"""

    observation_text: str


class FinalAnswer(BaseModel):
    reached_final_answer: bool


class Exit(BaseModel):
    exit: bool


class Functions:
    functions = [
        {
            "name": "Action",
            "description": "Search for a particular text in the knowledge base.",
            "parameters": Action.schema(),
        },
        {
            "name": "Thought",
            "description": "Generate a thought text with past history.",
            "parameters": Thought.schema(),
        },
        {
            "name": "Observation",
            "description": "Generate an observation text with past history.",
            "parameters": Observation.schema(),
        },
        {
            "name": "FinalAnswer",
            "description": "Based on the history tell if the final answer can be reached",
            "parameters": FinalAnswer.schema(),
        },
        {
            "name": "Exit",
            "description": "Exit the process",
            "parameters": Exit.schema(),
        },
    ]
