from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import HelperUpdate, HelperResponseBase, HelperProfile, HelperUpdateResponse
from app.auth.dependencies import get_current_user
from app.services.helper import (
    update_profile,
    delete_account,
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.get('/me', response_model=HelperProfile)
def read_current_helper(
    current_user = Depends(get_current_user)
):
    if current_user['role'] != 'helper':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Access permitted only for helpers'
        )
    logger.info(f'Success : {current_user}')
    return current_user['user']


@router.patch('/', response_model=HelperUpdateResponse)
def update_helper_data(
    helper_data: HelperUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user['role'] != 'helper':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Access permitted only for helpers'
        )
    updated_helper = update_profile(current_user['user'].id, helper_data, db)
    return updated_helper


@router.delete('/', response_model=dict)
def delete_helper(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user['role'] != 'helper':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Access permitted only for helpers'
        )
    delete_account(current_user['user'].id, db)
    return {'message': 'Account deleted successfully'}
