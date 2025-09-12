from fastapi import APIRouter 
# app/routes/onboarding.py 

route = APIRouter(prefix="/api/v1")


@route.get('/onboarding-config/{user_type}')
async def get_onboarding_config(user_type: str):


    configs ={
        "client": {
            "required_fields": ["name", "email", "password"],
            "optional_fields": [
                "phone", "cpf", "address", "city",
                "state", "postal_code", "country"
            ],
            "requires_verification": False,
            "can_use_immediately": True,
            "estimated_time_minutes": 2
        },

        "driver": {
            "required_fields": [
                "name", "email", "birth_date", "password",
                "car_model", "car_plate", "car_color",
                "driver_license", "license_category"
            ],
            "optional_fields": [
                "phone", "cpf", "address", "city",
                "state", "postal_code", "country",
                "rating", "is_active", "has_helpers",
                "helper_price", "is_blocked"
            ],
            "required_documents": ["driver_license_photo", "vehicle_document"],
            "requires_verification": True,
            "verification_time_hours": 24,
            "can_use_immediately": False,
            "estimated_time_minutes": 8
        },

        "helper": {
            "required_fields": ["name", "email", "birth_date", "password"],
            "optional_fields": [
                "phone", "cpf", "address", "city",
                "state", "postal_code", "country",
                "rating", "is_active", "is_blocked"
            ],
            "requires_verification": False,
            "can_use_immediately": True,
            "estimated_time_minutes": 3
        }
    }

    return configs.get(user_type, {})