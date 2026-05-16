# Vet Registration and Admin Verification Setup

## Overview
Implemented a complete vet registration flow where:
- Vets upload their license PDF during registration
- Vets cannot login until admin confirms their account
- Admin can verify or reject pending vet registrations

## Changes Made

### 1. Database Model (apps/vets/models.py)
Added `is_admin_verified` field to VetProfile:
```python
is_admin_verified = models.BooleanField(default=False, db_index=True)
```
- Default value: False (vets are not verified initially)
- Indexed for faster queries when filtering pending vets

### 2. Authentication (apps/users/serializers.py)
Updated `PetsoTokenObtainPairSerializer` to block vet login:
- Vets must have `vet_profile.is_admin_verified = True` to login
- Returns error: "Your account is pending admin verification. Please wait for confirmation."
- Other roles (farmer, company, admin) are unaffected

### 3. Serializers (apps/vets/serializers.py)

#### VetProfileSerializer
- Updated to include `is_admin_verified` field (read-only)
- Made certain fields read-only to prevent unauthorized changes

#### VetRegistrationSerializer (NEW)
Handles vet registration with:
- **User fields**: email, name, password, phone_number
- **License fields**: license_number, license_document (PDF required)
- **Profile fields**: specialties, qualifications, clinic_address, years_of_experience
- **Optional fields**: gps_lat, gps_long
- **Validation**: Ensures license_document is a PDF file
- **Atomic transaction**: Creates both User and VetProfile together

### 4. API Endpoints

#### POST /api/vets/register/
**Vet Registration Endpoint**
- Accepts multipart/form-data for file upload
- Creates user account with role='vet'
- Creates VetProfile with license document
- Sets `is_admin_verified = False`
- Sends confirmation email (optional, auto-verifies if email fails)
- No login required

**Request Body:**
```json
{
  "email": "vet@example.com",
  "name": "Dr. John Smith",
  "password": "securepassword",
  "phone_number": "+1234567890",
  "license_number": "VET123456",
  "license_document": <pdf_file>,
  "specialties": "Poultry Specialist",
  "qualifications": "DVM, University of XYZ",
  "clinic_address": "123 Clinic St, City",
  "years_of_experience": 5,
  "gps_lat": 40.7128,
  "gps_long": -74.0060
}
```

**Response:**
```json
{
  "id": 1,
  "user": {...},
  "license_number": "VET123456",
  "license_document": "/media/vets/licenses/...",
  "specialties": "Poultry Specialist",
  "qualifications": "DVM, University of XYZ",
  "clinic_address": "123 Clinic St, City",
  "years_of_experience": 5,
  "available": true,
  "rating": 0.0,
  "gps_lat": 40.7128,
  "gps_long": -74.0060,
  "is_admin_verified": false,
  "created_at": "2024-05-17T...",
  "updated_at": "2024-05-17T...",
  "message": "Registration successful. Please check your email to confirm your account. Your account is pending admin verification."
}
```

#### GET /api/vets/pending-verification/
**List Pending Vets for Admin**
- Admin-only endpoint
- Returns all vets with `is_admin_verified = False`
- Ordered by newest first
- Includes full vet profile and user information
- Requires admin permissions

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "email": "vet@example.com",
      "name": "Dr. John Smith",
      "phone_number": "+1234567890",
      "role": "vet",
      "is_verified": true,
      "date_joined": "2024-05-17T..."
    },
    "license_number": "VET123456",
    "license_document": "/media/vets/licenses/...",
    "specialties": "Poultry Specialist",
    "qualifications": "DVM, University of XYZ",
    "clinic_address": "123 Clinic St, City",
    "years_of_experience": 5,
    "is_admin_verified": false,
    "created_at": "2024-05-17T...",
    ...
  }
]
```

#### POST /api/vets/{vet_id}/admin-verify/
**Verify/Confirm a Vet (Admin Only)**
- Admin-only endpoint
- Sets `is_admin_verified = True`
- Vet can now login
- Returns confirmation details

**Response:**
```json
{
  "detail": "Vet verified successfully.",
  "vet_id": 1,
  "user_email": "vet@example.com",
  "user_name": "Dr. John Smith",
  "is_admin_verified": true
}
```

#### DELETE /api/vets/{vet_id}/admin-reject/
**Reject/Delete a Vet Registration (Admin Only)**
- Admin-only endpoint
- Permanently deletes the vet profile and user account
- Used to reject pending vet registrations
- Returns confirmation details

**Response:**
```json
{
  "detail": "Vet registration rejected and deleted.",
  "user_email": "vet@example.com"
}
```

## Database Migration

Migration created: `apps/vets/migrations/0003_vetprofile_is_admin_verified.py`
- Adds `is_admin_verified` BooleanField with default False
- Adds database index for performance

Applied successfully: Run `python manage.py migrate vets`

## User Flow

### Vet Registration Flow:
1. Vet calls POST `/api/vets/register/` with license PDF
2. User account created with role='vet', is_admin_verified=False
3. VetProfile created with license document
4. Confirmation email sent
5. Vet cannot login (blocked by PetsoTokenObtainPairSerializer)
6. Vet account is "pending admin verification"

### Admin Verification Flow:
1. Admin views POST `/api/vets/pending-verification/` to see all pending vets
2. Admin reviews vet profiles and license documents
3. Admin calls POST `/api/vets/{vet_id}/admin-verify/` to approve, OR
   Admin calls DELETE `/api/vets/{vet_id}/admin-reject/` to reject
4. If approved: Vet can now login
5. If rejected: Vet account is deleted

### Vet Login (After Admin Approval):
1. Vet confirms email (via email link)
2. Vet calls POST `/api/auth/login/` with credentials
3. PetsoTokenObtainPairSerializer checks:
   - Email is verified ✓
   - Role is 'vet' and vet_profile.is_admin_verified is True ✓
4. JWT tokens returned, vet is logged in

## Testing

### Test Vet Registration:
```bash
curl -X POST http://localhost:8000/api/vets/register/ \
  -F "email=vet@example.com" \
  -F "name=Dr. John Smith" \
  -F "password=securepassword" \
  -F "phone_number=+1234567890" \
  -F "license_number=VET123456" \
  -F "license_document=@license.pdf" \
  -F "specialties=Poultry Specialist" \
  -F "qualifications=DVM, University of XYZ" \
  -F "clinic_address=123 Clinic St, City" \
  -F "years_of_experience=5"
```

### Test Admin Verification:
```bash
# List pending vets (as admin)
curl -X GET http://localhost:8000/api/vets/pending-verification/ \
  -H "Authorization: Bearer <admin_token>"

# Verify a vet (as admin)
curl -X POST http://localhost:8000/api/vets/1/admin-verify/ \
  -H "Authorization: Bearer <admin_token>"

# Reject a vet (as admin)
curl -X DELETE http://localhost:8000/api/vets/1/admin-reject/ \
  -H "Authorization: Bearer <admin_token>"
```

### Test Login Blocking:
```bash
# Before admin approval (should fail)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "vet@example.com", "password": "securepassword"}'
# Returns: "Your account is pending admin verification. Please wait for confirmation."

# After admin approval (should succeed)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "vet@example.com", "password": "securepassword"}'
# Returns: JWT tokens
```

## Security Considerations

1. **File Upload**: Only PDF files are accepted for license documents
2. **Admin-Only Endpoints**: Verification/rejection endpoints require IsAdminUser permission
3. **Atomic Transactions**: User and VetProfile are created together
4. **Email Verification**: Vets must verify email before login (existing mechanism)
5. **Admin Verification**: Separate requirement from email verification for vets

## Features Summary

✅ Vet registration with license PDF upload
✅ Vets blocked from login until admin confirms
✅ Admin can view all pending vet registrations
✅ Admin can approve or reject vets
✅ Email confirmation still required
✅ Proper error messages
✅ RESTful API design
✅ Database migration included
✅ Atomic transactions for data integrity
