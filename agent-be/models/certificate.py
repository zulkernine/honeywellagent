from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class CertificateBase(BaseModel):
    cert_id: str
    subject: str
    issuer: str
    serial_number: str
    customer_name: str
    domain: str
    san: list[str] = []
    issued_at: datetime
    expires_at: datetime
    status: str = "active"          # active | expired | revoked | pending_renewal
    is_revoked: bool = False
    revocation_reason: Optional[str] = None
    revocation_date: Optional[datetime] = None
    key_algorithm: str = "RSA"
    key_size: int = 2048
    signature_algorithm: str = "SHA256withRSA"
    environment: str = "production"  # production | staging | dev
    tags: list[str] = []


class CertificateCreate(CertificateBase):
    pass


class Certificate(CertificateBase):
    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
