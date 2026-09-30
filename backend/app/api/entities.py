from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from ..graph import driver
from ..schemas.entity import (
    EntityProfile,
    EntitySearchResult,
    NetworkResponse,
    TimelineResponse,
)
from ..services.entity_service import (
    get_entity_profile,
    search_entities,
)
from ..services.network_service import (
    get_person_network,
)
from ..services.timeline_service import (
    get_person_timeline,
)


router = APIRouter(
    prefix="/entities",
    tags=["Entities"],
)


@router.get(
    "/search",
    response_model=list[
        EntitySearchResult
    ],
)
def search_entity_catalog(
    q: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    limit: int = Query(
        20,
        ge=1,
        le=50,
    ),
):

    return search_entities(driver, q, limit)


@router.get(
    "/{entity_id}",
    response_model=EntityProfile,
)
def get_entity(
    entity_id: str,
):

    entity = get_entity_profile(driver, entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Entity not found.")
    return entity


@router.get(
    "/{entity_id}/network",
    response_model=NetworkResponse,
)
def get_entity_network(
    entity_id: str,
    depth: int = Query(
        1,
        ge=1,
        le=2,
    ),
    node_limit: int = Query(250, ge=1, le=500),
    edge_limit: int = Query(500, ge=1, le=1000),
):

    # The first frontend version is
    # person-centric.
    if not entity_id.startswith("P"):
        raise HTTPException(
            status_code=400,
            detail=(
                "Network exploration currently "
                "supports Person entities."
            ),
        )

    network = get_person_network(driver, entity_id, depth, node_limit, edge_limit)
    if network is None:
        raise HTTPException(status_code=404, detail="Person not found.")
    return network


@router.get(
    "/{entity_id}/timeline",
    response_model=TimelineResponse,
)
def get_entity_timeline(
    entity_id: str,
    limit: int = Query(
        200,
        ge=1,
        le=500,
    ),
):

    if not entity_id.startswith("P"):
        raise HTTPException(
            status_code=400,
            detail=(
                "Timeline currently supports "
                "Person entities."
            ),
        )

    profile = get_entity_profile(driver, entity_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Person not found.")
    timeline = get_person_timeline(driver, entity_id, limit)
    return {"entity_id": entity_id, "items": timeline}