from typing import Tuple, List
from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlmodel import select, Session

from app.db import get_db
from app.models import CreateLocation, Location, Organisation, CreateOrganisation

router = APIRouter()

@router.post("/create", response_model=Organisation)
def create_organisation(create_organisation: CreateOrganisation, session: Session = Depends(get_db)) -> Organisation:
    """Create an organisation."""
    organisation = Organisation(name=create_organisation.name)
    session.add(organisation)
    session.commit()
    session.refresh(organisation)
    return organisation


@router.get("/", response_model=list[Organisation])
def get_organisations(session: Session = Depends(get_db)) -> list[Organisation]:
    """
    Get all organisations.
    """
    organisations = session.exec(select(Organisation)).all()
    return organisations



@router.get("/{organisation_id}", response_model=Organisation)
def get_organisation(organisation_id: int, session: Session = Depends(get_db)) -> Organisation:
    """
    Get an organisation by id.
    """
    organisation = session.get(Organisation, organisation_id)
    if organisation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return organisation


@router.post("/create/locations", response_model=Location) 
def create_location(create_location: CreateLocation,session: Session = Depends(get_db))-> Location:
    location = Location(
        organisation_id = create_location.organisation_id,
        location_name = create_location.location_name,
        longitude = create_location.longitude,
        latitude = create_location.latitude,
    )
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@router.get("/{organisation_id}/locations")
def get_organisation_locations(organisation_id: int, 
session: Session = Depends(get_db), 
bounding_box: Tuple[float, float, float, float] | None = Query(None, 
description="min_long, max_long, min_lat, max_lat"))->List[Location]:
    
    #Check organisation exists
    org = session.exec(select(Organisation).where(Organisation.id == organisation_id)).first()
    if not org:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Organisation does not exists")
    
    if bounding_box:
        min_long, max_long, min_lat, max_lat = bounding_box
        res = session.exec(select(Location)
                           .filter(Location.organisation_id == organisation_id)
                           .filter(
                            Location.longitude >= min_long,
                            Location.longitude <= max_long,
                            Location.latitude >= min_lat,
                            Location.latitude <= max_lat)
                            )
        return res.all()
    else:
        res = session.exec(select(Location)
                           .filter(Location.organisation_id == organisation_id))
        return res.all()

