from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.helper import HelperCreate, HelperUpdate, HelperResponse
from app.auth.auth_service import create_access_token
from app.services.helper import (
    create_helper,
    update_profile,
    delete_account,
)

router = APIRouter()
security = HTTPBearer()


@router.post('/', response_model=HelperResponse)
def new_helper(
    new_create_helper: HelperCreate,
    db: Session = Depends(get_db) 
):
    helper = create_helper(new_create_helper, db)
    token = create_access_token({'sub':str(helper.id)})
    return {
        'helper_id':helper.id,
        'access_token': token,
        'token_type': 'bearer',
        'message': 'Helper successfully registered !'
    }


@router.get('/me', response_model=HelperResponse)
def read_current_helper(
    current_user = Depends(security)
):
    if current_user['role'] != 'helper':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Access permitted only for helpers'
        )
    return {'helper': current_user['user']}


@router.put('/', response_model=HelperResponse)
def update_helper_data(
    helper_data: HelperUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(security)
):
    if current_user['role'] != 'helper':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Access permitted only for helpers'
        )
    updated_helper = update_profile(current_user['user'].id, helper_data, db)
    return {'helper': updated_helper}


@router.delete('/', response_model=dict)
def delete_helper(
    db: Session = Depends(get_db),
    current_user = Depends(security)
):
    if current_user['role'] != 'helper':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Access permitted only for helpers'
        )
    delete_account(current_user['user'].id, db)
    return {'message': 'Account deleted successfully'}
