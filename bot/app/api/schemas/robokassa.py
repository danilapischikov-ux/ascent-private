from pydantic import BaseModel


class RobokassaResultResponse(BaseModel):
    result: str
