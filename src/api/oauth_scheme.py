# Third party
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Local
from ..config import settings
from ..serializers import TokenData

oauth2_scheme = HTTPBearer(auto_error=True)

####################################################################################################
# FUNCTIONS
####################################################################################################

def verify_token(access_token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> TokenData:
    invalid_token = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(access_token.credentials, settings.get_secret_key, algorithms=[settings.JWT_ALGORITHM])
        user_id: str | None = payload.get("sub")
        type_: str | None = payload.get("type")
        if user_id is None or type_ != "access":
            raise invalid_token

        return TokenData(sub=user_id)
    except InvalidTokenError:
        raise invalid_token