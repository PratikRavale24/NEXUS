from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class EntitySearchResult(BaseModel):
    entity_id: str
    entity_type: str
    name: str
    secondary_identifier: str | None = None


class EntityProfile(BaseModel):
    entity_id: str
    entity_type: str
    name: str

    properties: dict = Field(
        default_factory=dict
    )

    connection_count: int = 0
    finding_count: int = 0


class NetworkNode(BaseModel):
    id: str
    entity_type: str
    label: str

    properties: dict = Field(
        default_factory=dict
    )


class NetworkEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship: str

    properties: dict = Field(
        default_factory=dict
    )


class NetworkResponse(BaseModel):
    root_entity_id: str
    depth: int

    nodes: list[NetworkNode] = Field(
        default_factory=list
    )

    edges: list[NetworkEdge] = Field(
        default_factory=list
    )


class TimelineItem(BaseModel):
    timestamp: datetime | None = None

    event_type: str
    description: str

    entity_id: str | None = None
    entity_name: str | None = None

    related_entity_id: str | None = None
    related_entity_name: str | None = None

    case_id: str | None = None
    evidence_id: str | None = None

    source_type: str | None = None


class TimelineResponse(BaseModel):
    entity_id: str
    items: list[TimelineItem] = Field(
        default_factory=list
    )