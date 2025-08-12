from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlmodel import select
import secrets as pysecrets
import os

from app.database import SessionDep
from app.elwis_api import fetch_all_messages_for_day
from app.logger import get_logger
from app.models.cache import CacheMetadata
from app.models.ftm import (
    ElwisFtm,
    Fairway,
    FairwaySection,
    get_fairway_sections,
)

logger = get_logger()

router = APIRouter(prefix="/cache", tags=["Cache"])

security = HTTPBasic()


class CacheMetadataResponse(BaseModel):
    last_updated: datetime


@router.get("")
def get_cache_info(session: SessionDep) -> CacheMetadataResponse:
    cache_metadata = session.exec(select(CacheMetadata)).first()
    if not cache_metadata:
        raise HTTPException(status_code=404, detail="Cache metadata not found")
    return CacheMetadataResponse(last_updated=cache_metadata.last_updated)


@router.post("/update", status_code=204)
def update_cache(
    session: SessionDep,
    credentials: HTTPBasicCredentials = Depends(security),
) -> None:
    # Read credentials from secrets file or env
    username_path = "/run/secrets/cache_update_user"
    password_path = "/run/secrets/cache_update_password"
    try:
        with open(username_path) as f:
            expected_username = f.read().strip()
        with open(password_path) as f:
            expected_password = f.read().strip()
    except Exception:
        expected_username = os.getenv("CACHE_UPDATE_USER", "admin")
        expected_password = os.getenv("CACHE_UPDATE_PASSWORD", "admin")

    correct_username = pysecrets.compare_digest(credentials.username, expected_username)
    correct_password = pysecrets.compare_digest(credentials.password, expected_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    logger.info("Updating cache...")
    cache_metadata = session.exec(select(CacheMetadata)).first()
    if not cache_metadata:
        cache_metadata = CacheMetadata()

    messages = fetch_all_messages_for_day(datetime.now(timezone.utc).date())
    for message in messages:
        fairway_sections = get_fairway_sections(message)

        for fairway_section in fairway_sections:
            db_fairway_section = session.exec(
                select(FairwaySection)
                .where(FairwaySection.ftm_year == fairway_section.ftm_message.year)
                .where(FairwaySection.ftm_number == fairway_section.ftm_message.number)
                .where(
                    FairwaySection.ftm_serial_number
                    == fairway_section.ftm_message.serial_number
                )
                .where(FairwaySection.fairway_name == fairway_section.fairway.name)
                .where(
                    FairwaySection.start_hectometer == fairway_section.start_hectometer
                )
                .where(FairwaySection.end_hectometer == fairway_section.end_hectometer)
            ).first()

            if db_fairway_section:
                continue

            db_fairway = session.exec(
                select(Fairway).where(Fairway.name == fairway_section.fairway.name)
            ).first()

            if db_fairway:
                fairway_section.fairway = db_fairway
            else:
                session.add(fairway_section.fairway)
                logger.debug(f"Added new fairway {fairway_section.fairway.name}")

            db_message = session.exec(
                select(ElwisFtm)
                .where(ElwisFtm.year == fairway_section.ftm_message.year)
                .where(ElwisFtm.number == fairway_section.ftm_message.number)
                .where(
                    ElwisFtm.serial_number == fairway_section.ftm_message.serial_number
                )
            ).first()

            if db_message:
                fairway_section.ftm_message = db_message
            else:
                session.add(fairway_section.ftm_message)
                logger.debug(
                    f"Added new FTM message {fairway_section.ftm_message.year}-{fairway_section.ftm_message.number}-{fairway_section.ftm_message.serial_number}"
                )

            session.add(fairway_section)
            logger.debug(
                f"Added new fairway section {fairway_section.fairway.name} for FTM {fairway_section.ftm_message.year}-{fairway_section.ftm_message.number}-{fairway_section.ftm_message.serial_number}"
            )

    cache_metadata.last_updated = datetime.now(timezone.utc)

    session.add(cache_metadata)
    try:
        session.commit()
    except Exception as e:
        logger.error(f"Error committing session: {e}")
        session.rollback()
        raise
