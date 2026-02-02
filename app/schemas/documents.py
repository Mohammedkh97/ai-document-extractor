"""
Document schema definitions using Pydantic.
These schemas define the structure of extracted document data.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types for extraction."""
    CONTRACT = "EMPLOYMENT CONTRACT FULL WORK"
    TOURISM_VISA = "eVisa - Tourism"
    EMPLOYMENT_VISA = "eVisa - Employment"
    RESIDENCE = "Residence"
    CHANGE_STATUS = "Change Status"
    HEALTHCARE = "Healthcare Professional Registration Certificate"
    PASSPORT = "Passport"
    TENANCY_CONTRACT = "Tenancy Contract"
    GRADUATION_CERTIFICATE = "Graduation Certificate"
    DRIVING_LICENSE = "Driving License"
    UNKNOWN = "Unknown"


class ContractData(BaseModel):
    """Employment contract extracted data."""
    work_style: Optional[str] = Field(
        None, description="Type of work (e.g., Full time, Part time, Temporary)"
    )
    transaction_number: Optional[str] = Field(
        None, description="Transaction number used by MOHRE"
    )
    name: Optional[str] = Field(None, description="Full legal name of the employee")
    nationality: Optional[str] = Field(None, description="Nationality of the employee")
    passport_number: Optional[str] = Field(None, description="Passport number")
    date_of_birth: Optional[str] = Field(
        None, description="Date of birth (DD/MM/YYYY)"
    )
    academic_qualification: Optional[str] = Field(
        None, description="Academic qualification"
    )
    contract_start: Optional[str] = Field(
        None, description="Start date of the contract (DD/MM/YYYY)"
    )
    contract_end: Optional[str] = Field(
        None, description="End date of the contract (DD/MM/YYYY)"
    )


class VisaData(BaseModel):
    """Visa (Tourism/Employment) extracted data."""
    issue_date: Optional[str] = Field(
        None, description="Visa issue date (DD/MM/YYYY)"
    )
    place_of_issue: Optional[str] = Field(
        None, description="Place where the visa was issued"
    )
    valid_until: Optional[str] = Field(
        None, description="Visa expiration date (DD/MM/YYYY)"
    )
    uid_number: Optional[str] = Field(
        None, description="UID number (9 to 15 digits)"
    )
    full_name: Optional[str] = Field(None, description="Full name of the visa holder")
    nationality: Optional[str] = Field(None, description="Nationality")
    place_of_birth: Optional[str] = Field(None, description="Place of birth")
    date_of_birth: Optional[str] = Field(
        None, description="Date of birth (DD/MM/YYYY)"
    )
    passport_number: Optional[str] = Field(None, description="Passport number")
    profession: Optional[str] = Field(None, description="Profession listed on visa")


class ResidenceData(BaseModel):
    """Residence permit extracted data."""
    id_number: Optional[str] = Field(
        None, description="Residence ID number (numeric)"
    )
    passport_number: Optional[str] = Field(None, description="Passport number")
    name: Optional[str] = Field(None, description="Full name")
    profession: Optional[str] = Field(None, description="Profession")
    issue_date: Optional[str] = Field(
        None, description="Issue date (DD/MM/YYYY)"
    )
    expiry_date: Optional[str] = Field(
        None, description="Expiration date (DD/MM/YYYY)"
    )


class ChangeStatusData(BaseModel):
    """Change status document extracted data."""
    uid_number: Optional[str] = Field(None, description="UID number")
    name: Optional[str] = Field(None, description="Full name")
    nationality: Optional[str] = Field(None, description="Nationality")
    profession: Optional[str] = Field(None, description="Profession")
    passport_number: Optional[str] = Field(None, description="Passport number")
    employer_name: Optional[str] = Field(None, description="Employer name")
    residence_stamping_deadline: Optional[str] = Field(
        None, description="Deadline for residence stamping (DD/MM/YYYY)"
    )


class HealthcareRegistrationData(BaseModel):
    """Healthcare professional registration certificate extracted data."""
    professional_name: Optional[str] = Field(
        None, description="Name of healthcare professional"
    )
    dha_unique_id: Optional[str] = Field(
        None, description="DHA Unique Identifier"
    )


class PassportData(BaseModel):
    """Passport extracted data."""
    passport_number: Optional[str] = Field(None, description="Passport number")
    name: Optional[str] = Field(None, description="Full name on passport")
    date_of_birth: Optional[str] = Field(
        None, description="Date of birth (DD/MM/YYYY)"
    )
    date_of_issue: Optional[str] = Field(
        None, description="Date of issue (DD/MM/YYYY)"
    )
    date_of_expiry: Optional[str] = Field(
        None, description="Date of expiry (DD/MM/YYYY)"
    )
    profession: Optional[str] = Field(None, description="Profession listed")
    nationality: Optional[str] = Field(None, description="Nationality")
    place_of_birth: Optional[str] = Field(None, description="Place of birth")

class GraduationCertificateData(BaseModel):
    """Graduation certificate extracted data."""
    name: Optional[str] = Field(None, description="Full name")
    
class TenancyContractData(BaseModel):
    """Tenancy contract extracted data."""
    tenant_name: Optional[str] = Field(None, description="Name of tenant")
    property_no: Optional[str] = Field(None, description="Property number")
    start_date: Optional[str] = Field(
        None, description="Contract start date (DD/MM/YYYY)"
    )
    end_date: Optional[str] = Field(
        None, description="Contract end date (DD/MM/YYYY)"
    )
    license_no: Optional[str] = Field(None, description="License number")
    registration_date: Optional[str] = Field(
        None, description="Registration date (DD/MM/YYYY)"
    )
    expiry_date: Optional[str] = Field(
        None, description="Expiry date (DD/MM/YYYY)"
    )


class GraduationCertificateData(BaseModel):
    """Graduation certificate extracted data."""
    full_name: Optional[str] = Field(None, description="Full Name")
    nationality: Optional[str] = Field(None, description="Nationality")
    date_of_birth: Optional[str] = Field(
        None, description="Date of birth (DD/MM/YYYY)"
    )
    cumulative_estimation: Optional[str] = Field(
        None, description="Cumulative estimation (acceptable, good, very good, excellent)"
    )
    major: Optional[str] = Field(None, description="College and university major")
    gpa: Optional[str] = Field(None, description="GPA")
    graduation_year: Optional[str] = Field(None, description="Year Of Graduation")
    university_name: Optional[str] = Field(None, description="Name Of University")


class DrivingLicenseData(BaseModel):
    """Driving license extracted data."""
    country_name: Optional[str] = Field(None, description="Country name")
    full_name: Optional[str] = Field(None, description="FullName")
    nationality: Optional[str] = Field(None, description="Nationality")
    date_of_birth: Optional[str] = Field(
        None, description="Date Of Birth (DD/MM/YYYY)"
    )
    issue_date: Optional[str] = Field(
        None, description="Issue Date (DD/MM/YYYY)"
    )
    expiry_date: Optional[str] = Field(
        None, description="Expiry Date (DD/MM/YYYY)"
    )
    place_of_issue: Optional[str] = Field(None, description="Place Of Issue")


class DocumentSchema(BaseModel):
    """
    Unified document schema for all document types.
    Only the relevant details field will be populated based on document_type.
    """
    document_type: DocumentType = Field(..., description="The detected document type")
    contract_details: Optional[ContractData] = Field(
        None, description="Extracted contract details"
    )
    visa_details: Optional[VisaData] = Field(
        None, description="Extracted visa details"
    )
    residence_details: Optional[ResidenceData] = Field(
        None, description="Extracted residence details"
    )
    change_status_details: Optional[ChangeStatusData] = Field(
        None, description="Extracted change status details"
    )
    healthcare_details: Optional[HealthcareRegistrationData] = Field(
        None, description="Extracted healthcare details"
    )
    passport_details: Optional[PassportData] = Field(
        None, description="Extracted passport details"
    )
    tenancy_details: Optional[TenancyContractData] = Field(
        None, description="Extracted tenancy contract details"
    )
    graduation_details: Optional[GraduationCertificateData] = Field(
        None, description="Extracted graduation certificate details"
    )
    driving_license_details: Optional[DrivingLicenseData] = Field(
        None, description="Extracted driving license details"
    )

# Mapping from document type to the relevant details field
DOCUMENT_TYPE_FIELD_MAP = {
    DocumentType.CONTRACT: "contract_details",
    DocumentType.TOURISM_VISA: "visa_details",
    DocumentType.EMPLOYMENT_VISA: "visa_details",
    DocumentType.RESIDENCE: "residence_details",
    DocumentType.CHANGE_STATUS: "change_status_details",
    DocumentType.HEALTHCARE: "healthcare_details",
    DocumentType.PASSPORT: "passport_details",
    DocumentType.TENANCY_CONTRACT: "tenancy_details",
    DocumentType.GRADUATION_CERTIFICATE: "graduation_details",
    DocumentType.DRIVING_LICENSE: "driving_license_details",
}
