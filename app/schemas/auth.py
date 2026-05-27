from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)
    nickname: str = Field(default="", max_length=50)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=50)
    avatar: str | None = Field(default=None, max_length=500)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=50)


class UserOut(BaseModel):
    id: int
    email: str
    nickname: str
    avatar: str | None = None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    user: UserOut
    token: str
    token_type: str = "Bearer"
    expires_in: int
