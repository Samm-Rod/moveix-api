import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import date
from app.services.helper import create_helper

from app.schemas.helper import HelperCreate
from app.models.helper import Helper 
from app.utils.hashing import hash_password
from app.auth.two_f import generate_2fa_code

# Terminar em casa dia 28/07/2025 às 01:33h 
def sample_helper_data():
    ...

def test_create_new_driver_success():
    ...