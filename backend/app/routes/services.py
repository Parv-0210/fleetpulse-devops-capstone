from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ServiceRecord

router = APIRouter(prefix="/api/services", tags=["services"])


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a service record")
def delete_service(record_id: int, db: Session = Depends(get_db)):
    record = db.get(ServiceRecord, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Service record not found")
    db.delete(record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
