# Vet Registration & Admin Verification - Quick Start Guide

## Endpoints Summary

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/api/vets/register/` | Register new vet with license PDF | No |
| GET | `/api/vets/pending-verification/` | List vets pending admin approval | Admin Only |
| POST | `/api/vets/{vet_id}/admin-verify/` | Approve a vet registration | Admin Only |
| DELETE | `/api/vets/{vet_id}/admin-reject/` | Reject/delete a vet registration | Admin Only |

## Step-by-Step Implementation Guide

### Step 1: Vet Registration (Frontend)

**Create a form with:**
- Email field
- Name field
- Password field (min 8 chars)
- Phone number field (optional)
- License number field
- License PDF file upload (required - PDF only)
- Specialties field (e.g., "Poultry Specialist")
- Qualifications field (e.g., "DVM, University Name")
- Clinic address field
- Years of experience field (number)
- GPS coordinates fields (optional)

**API Request:**
```javascript
const formData = new FormData();
formData.append('email', 'vet@example.com');
formData.append('name', 'Dr. John Smith');
formData.append('password', 'SecurePass123');
formData.append('phone_number', '+1234567890');
formData.append('license_number', 'VET123456');
formData.append('license_document', pdfFile); // File object
formData.append('specialties', 'Poultry Specialist');
formData.append('qualifications', 'DVM, University of Lagos');
formData.append('clinic_address', '123 Clinic Street, City');
formData.append('years_of_experience', '5');
formData.append('gps_lat', '6.5244');
formData.append('gps_long', '3.3792');

const response = await fetch('/api/vets/register/', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.message); // Registration successful message
```

**Success Response (201):**
```json
{
  "id": 1,
  "user": {
    "id": 15,
    "email": "vet@example.com",
    "name": "Dr. John Smith",
    "phone_number": "+1234567890",
    "role": "vet",
    "is_verified": false,
    "date_joined": "2024-05-17T10:30:00Z"
  },
  "license_number": "VET123456",
  "license_document": "http://localhost:8000/media/vets/licenses/license_abc123.pdf",
  "specialties": "Poultry Specialist",
  "qualifications": "DVM, University of Lagos",
  "clinic_address": "123 Clinic Street, City",
  "years_of_experience": 5,
  "available": true,
  "rating": 0.0,
  "gps_lat": "6.5244",
  "gps_long": "3.3792",
  "is_admin_verified": false,
  "created_at": "2024-05-17T10:30:00Z",
  "updated_at": "2024-05-17T10:30:00Z",
  "message": "Registration successful. Please check your email to confirm your account. Your account is pending admin verification."
}
```

**Error Response (400):**
```json
{
  "email": ["This field may not be blank."],
  "license_document": ["License document must be a PDF file."]
}
```

### Step 2: Email Confirmation (Frontend)

After registration, vet receives an email with a confirmation link:
```
Click here to confirm your email: http://localhost:8000/api/auth/confirm-email/<UUID_TOKEN>/
```

Vet clicks the link to verify email. The response shows a confirmation page.

### Step 3: Admin Reviews Pending Vets

**Admin gets list of vets waiting for approval:**

```javascript
const token = 'admin_jwt_token';

const response = await fetch('/api/vets/pending-verification/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const pendingVets = await response.json();
console.log(pendingVets);
```

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 15,
      "email": "vet@example.com",
      "name": "Dr. John Smith",
      "phone_number": "+1234567890",
      "role": "vet",
      "is_verified": true,
      "date_joined": "2024-05-17T10:30:00Z"
    },
    "license_number": "VET123456",
    "license_document": "http://localhost:8000/media/vets/licenses/license_abc123.pdf",
    "specialties": "Poultry Specialist",
    "qualifications": "DVM, University of Lagos",
    "clinic_address": "123 Clinic Street, City",
    "years_of_experience": 5,
    "available": true,
    "rating": 0.0,
    "gps_lat": "6.5244",
    "gps_long": "3.3792",
    "is_admin_verified": false,
    "created_at": "2024-05-17T10:30:00Z",
    "updated_at": "2024-05-17T10:30:00Z"
  }
]
```

**Admin can:**
- View vet profile and qualifications
- Download and review the license PDF document
- Decide to approve or reject

### Step 4: Admin Approves Vet

```javascript
const vetId = 1;
const token = 'admin_jwt_token';

const response = await fetch(`/api/vets/${vetId}/admin-verify/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const result = await response.json();
console.log(result);
// {
//   "detail": "Vet verified successfully.",
//   "vet_id": 1,
//   "user_email": "vet@example.com",
//   "user_name": "Dr. John Smith",
//   "is_admin_verified": true
// }
```

After approval, **vet can now login**.

### Step 5: Admin Rejects Vet

```javascript
const vetId = 1;
const token = 'admin_jwt_token';

const response = await fetch(`/api/vets/${vetId}/admin-reject/`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const result = await response.json();
console.log(result);
// {
//   "detail": "Vet registration rejected and deleted.",
//   "user_email": "vet@example.com"
// }
```

The vet account and profile are permanently deleted.

### Step 6: Vet Attempts Login

**Before Admin Approval (Should Fail):**
```javascript
const response = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'vet@example.com',
    password: 'SecurePass123'
  })
});

const data = await response.json();
// {
//   "detail": "Your account is pending admin verification. Please wait for confirmation."
// }
```

**After Admin Approval (Should Succeed):**
```javascript
const response = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'vet@example.com',
    password: 'SecurePass123'
  })
});

const data = await response.json();
// {
//   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
//   "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
//   "user_id": 15,
//   "email": "vet@example.com",
//   "name": "Dr. John Smith",
//   "role": "vet"
// }
```

## Admin Dashboard Display Recommendation

Show a table with columns:
- Vet Name
- Email
- License Number
- Specialties
- Years of Experience
- Registration Date
- Status (⏳ Pending / ✅ Approved)
- Actions (View PDF | Approve | Reject)

When viewing a pending vet:
1. Show all profile details
2. Provide a button to download/view the license PDF
3. Show "Approve" and "Reject" buttons
4. Show registration timestamp

## Error Handling

| Error | Status | Message | Solution |
|-------|--------|---------|----------|
| Missing required field | 400 | Field validation error | Provide all required fields |
| Email already exists | 400 | Email already registered | Use different email |
| Invalid PDF | 400 | License document must be a PDF file | Upload a .pdf file |
| Already verified | 400 | This vet is already verified | Cannot verify twice |
| Not found | 404 | Vet profile not found | Check vet_id is correct |
| Unauthorized | 403 | Admin only | Must have admin token |

## Database Fields Reference

VetProfile model includes:
- `id` - Unique identifier
- `user_id` - Foreign key to User
- `license_number` - Vet's license number
- `license_document` - Uploaded PDF file
- `specialties` - Specialization areas
- `qualifications` - Educational credentials
- `clinic_address` - Clinic location
- `years_of_experience` - Years of experience
- `available` - Availability status (default: True)
- `rating` - Average rating (default: 0.0)
- `gps_lat` - Latitude (optional)
- `gps_long` - Longitude (optional)
- `is_admin_verified` - Admin confirmation status (default: False) ⭐ NEW
- `created_at` - Registration timestamp
- `updated_at` - Last update timestamp

## Security Notes

1. **File Upload**: Only PDF files accepted
2. **Email Verification**: Required before login (existing)
3. **Admin Verification**: Separate step for vets
4. **Permissions**: Each endpoint has appropriate permission checks
5. **Data Atomicity**: User and VetProfile created together

## Testing Checklist

- [ ] Vet can register with PDF
- [ ] Vet cannot login before email verification
- [ ] Vet cannot login before admin approval
- [ ] Admin can see pending vets
- [ ] Admin can approve vets
- [ ] Admin can reject vets
- [ ] Vet can login after approval
- [ ] Only PDF files accepted
- [ ] Email confirmation works
- [ ] Proper error messages shown
