from enum import Enum

class LicenseCategory(str, Enum):
    A = 'a'
    B = 'b'
    C = 'c'
    D = 'd'
    E = 'e'
    AB = 'ab'

class VehicleStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    UNDER_REVIEW = 'under_review'

class VehicleSize(str, Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'

    