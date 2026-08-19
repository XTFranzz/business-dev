import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import SavedSearch
from app.schemas.saved_search import SavedSearchCreate, SavedSearchRead

router = APIRouter(prefix="/saved-searches", tags=["saved-searches"])


@router.get("", response_model=list[SavedSearchRead])
def list_saved_searches(db: Session = Depends(get_db)) -> list[SavedSearch]:
    return (
        db.execute(select(SavedSearch).order_by(SavedSearch.created_at.desc())).scalars().all()
    )


@router.post("", response_model=SavedSearchRead, status_code=201)
def create_saved_search(payload: SavedSearchCreate, db: Session = Depends(get_db)) -> SavedSearch:
    params = {
        "country": payload.country,
        "state": payload.state,
        "city": payload.city,
        "category": payload.category,
        "max_results": payload.max_results,
    }
    saved_search = SavedSearch(name=payload.name, params=params)
    db.add(saved_search)
    db.commit()
    db.refresh(saved_search)
    return saved_search


@router.delete("/{saved_search_id}", status_code=204)
def delete_saved_search(saved_search_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    saved_search = db.get(SavedSearch, saved_search_id)
    if saved_search is None:
        raise HTTPException(status_code=404, detail="Saved search not found")
    db.delete(saved_search)
    db.commit()
