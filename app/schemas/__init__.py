from .client import (
        ClientBase, ClientCreate, ClientList, ClientProfile,
        ClientUpdate, ClientLogin, ClientRegisterResponse, ClientDeleteResponse
    )

from .driver import (
    DriverBase, DriverCreate, DriverList, DriverResponse, DriverResponseBase, 
    DriverDeleteResponse, DriverAuthResponse, DriverLogin, DriverUpdate
)

from .helper import (
    HelperAuthResponse, HelperBase, HelperCreate, HelperDeleteResponse, HelperList, 
    HelperLogin, HelperResponse, HelperResponseBase, HelperUpdate, HelperProfile, HelperUpdateResponse
)

from .auth import (
    TwoFAValidateRequest, DriverLogin, HelperLogin, ClientLogin,
    ForgotPasswordRequest, ResetPasswordRequest, Tokens
)

from .locations import (
    LocationBase, LocationCreate, LocationRead, 
    LocationResponse, ConfigDict
)

from .payments import (
    Optional, PaymentCreate, PaymentOut
)

from .quote import ( 
    QuoteOption, QuoteResponse, DynamicQuoteResponse, PriceBreakdown
)

from .ride import (
    Ride, RideBase,RideConfirmation, RideDeleteResponse, RideList, RideOption,
    RideQuoteResponse, RideRatingOut, RideResponse, RideUpdate,
    RequestRide
)

from .vehicle import (
    Vehicle, VehicleBase, VehicleChoose, VehicleCreate, VehicleList, VehicleRemove, 
    VehicleResponse, VehicleSize, VehicleStatus, VehicleUpdate
)


# --- Forçar rebuild dos schemas com referências cruzadas ---
from .driver import DriverResponse
from .helper import HelperResponse
from .client import ClientProfile

DriverResponse.model_rebuild()
HelperResponse.model_rebuild()
ClientProfile.model_rebuild()
