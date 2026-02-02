# Security Considerations

**Last Updated**: 2026-02-01  
**Threat Model**: Public-facing API with user authentication

---

## Overview

This document outlines the security measures implemented in Kitsune and known risks that require mitigation before production deployment.

---

## ✅ Implemented Security Measures

### 1. **Authentication**

#### JWT Tokens

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Storage**: Client-side (localStorage or httpOnly cookies recommended)

**Implementation**:

```python
# Token creation with expiration
def create_access_token(subject: str, expires_delta: timedelta):
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

**Security Properties**:

- ✅ Tokens are signed (tamper-proof)
- ✅ Tokens expire automatically
- ✅ Timezone-aware timestamps (no UTC bugs)

**Known Limitations**:

- ❌ No token revocation (can't invalidate before expiration)
- ❌ No refresh tokens (users must re-login every 30 min)

---

### 2. **Password Security**

#### Hashing

- **Algorithm**: Bcrypt
- **Rounds**: 12 (default, ~100ms per hash)
- **Salt**: Automatic (bcrypt generates unique salt per password)

**Why Bcrypt**:

- Resistant to rainbow table attacks (salted)
- Computationally expensive (slows brute-force)
- Adaptive (can increase rounds as hardware improves)

**Example**:

```python
# Hashing
hashed = get_password_hash("user_password")
# Result: $2b$12$random_salt$hashed_value

# Verification
is_valid = verify_password("user_password", hashed)
```

**Considerations**:

- Bcrypt has a 72-character limit (truncates longer passwords)
- 12 rounds may be too fast in 2026+ (consider 14 rounds)

---

### 3. **Input Validation**

#### Pydantic Schemas

All API inputs are validated before processing:

```python
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str    # Required, non-empty
    full_name: str
```

**Protection Against**:

- ✅ SQL Injection (parameterized queries via SQLAlchemy)
- ✅ Type confusion (Pydantic enforces types)
- ✅ Missing required fields

---

### 4. **CORS Configuration**

**Current State** (⚠️ **INSECURE BY DEFAULT**):

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Allows ANY origin
    allow_credentials=True,
)
```

**Production Fix Required**:

```python
# config.py
BACKEND_CORS_ORIGINS: list[str] = ["https://yourdomain.com"]

# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

### 5. **Docker Security**

#### Non-Root User

```dockerfile
RUN addgroup --system appuser && adduser --system --group appuser
USER appuser
```

**Why**: Limits damage if container is compromised.

#### Multi-Stage Build

```dockerfile
FROM python:3.11-slim as builder
# Build dependencies

FROM python:3.11-slim
# Only runtime files
```

**Why**: Reduces attack surface (no build tools in final image).

---

## ⚠️ Known Vulnerabilities (Requires Mitigation)

### 1. **SECRET_KEY Hardcoded** 🔴 **CRITICAL**

**Issue**: Default `SECRET_KEY` is predictable.

```python
# config.py
SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_TO_A_SECURE_SECRET_KEY"
```

**Impact**: Anyone can forge valid JWTs.

**Fix**:

```bash
# Generate secure key
openssl rand -hex 32

# Set in .env
SECRET_KEY=your_generated_key_here
```

**Validation** (add to `config.py`):

```python
@field_validator("SECRET_KEY")
@classmethod
def validate_secret_key(cls, v: str) -> str:
    if v == "CHANGE_THIS_IN_PRODUCTION_TO_A_SECURE_SECRET_KEY":
        raise ValueError("SECRET_KEY must be changed in production")
    if len(v) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters")
    return v
```

---

### 2. **No Rate Limiting** 🟠 **HIGH**

**Issue**: Endpoints are vulnerable to brute-force attacks.

**Attack Scenario**:

```bash
# Brute-force login
for password in wordlist.txt; do
  curl -X POST /api/v1/login/access-token \
    -d "username=admin@example.com&password=$password"
done
```

**Fix**: Implement rate limiting with Redis.

```python
# Install slowapi
# poetry add slowapi

# main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)
app.state.limiter = limiter

# endpoints/login.py
@router.post("/login/access-token")
@limiter.limit("5/minute")  # Max 5 attempts per minute
async def login(...):
    ...
```

---

### 3. **User Enumeration via Timing Attack** 🟠 **HIGH**

**Issue**: Login endpoint leaks whether a user exists.

**Current Code**:

```python
user = await db.execute(select(User).filter(User.email == email))
if not user:
    # Fast response (no bcrypt)
    raise HTTPException(400, "Incorrect email or password")

if not verify_password(password, user.hashed_password):
    # Slow response (~100ms bcrypt)
    raise HTTPException(400, "Incorrect email or password")
```

**Attack**: Measure response time to determine if email exists.

**Fix**:

```python
user = await db.execute(select(User).filter(User.email == email))

# Always verify hash (even if user doesn't exist)
if user:
    password_valid = verify_password(password, user.hashed_password)
else:
    # Dummy hash to maintain constant time
    verify_password(password, get_password_hash("dummy"))
    password_valid = False

if not password_valid or not user:
    raise HTTPException(401, "Incorrect email or password")
```

---

### 4. **SQL Injection (Low Risk)** 🟡 **MEDIUM**

**Current Protection**: SQLAlchemy uses parameterized queries.

**Safe**:

```python
# SQLAlchemy automatically escapes
query = select(User).filter(User.email == user_input)
```

**Unsafe** (if you do this):

```python
# ❌ NEVER DO THIS
query = f"SELECT * FROM users WHERE email = '{user_input}'"
```

**Recommendation**: Always use SQLAlchemy's query builder or ORM.

---

### 5. **No HTTPS Enforcement** 🟡 **MEDIUM**

**Issue**: API doesn't enforce HTTPS.

**Impact**: Tokens can be intercepted in transit.

**Fix**: Deploy behind a reverse proxy (Nginx, Traefik) with HTTPS.

```nginx
# nginx.conf
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://kitsune:8000;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

**Add HSTS header**:

```python
# main.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

### 6. **No Input Sanitization in Logs** 🟡 **MEDIUM**

**Issue**: Sensitive data might leak into logs.

**Example**:

```python
# ❌ BAD: Logs password
logger.info(f"User login attempt: {form_data}")

# ✅ GOOD: Sanitize
logger.info("user_login_attempt", email=form_data.username)
```

**Fix**: Never log passwords, tokens, or PII.

---

## 🔵 Accepted Risks (Documented)

### 1. **No Refresh Tokens**

**Risk**: Users must re-login every 30 minutes.

**Mitigation**: Short token lifetime limits damage if token is stolen.

**Roadmap**: Implement refresh tokens in v0.2.0.

---

### 2. **No Multi-Factor Authentication (MFA)**

**Risk**: Password-only authentication is less secure.

**Mitigation**: Enforce strong password policies (min length, complexity).

**Roadmap**: Add TOTP-based MFA in v1.0.0.

---

### 3. **No Audit Logging**

**Risk**: Can't track who did what and when.

**Mitigation**: Application logs capture request metadata.

**Roadmap**: Add audit log table in v0.3.0.

---

## 🛡️ Security Checklist (Pre-Production)

### Critical (Must Fix)

- [ ] Generate and set secure `SECRET_KEY`
- [ ] Configure `BACKEND_CORS_ORIGINS` with specific domains
- [ ] Enable HTTPS (via reverse proxy)
- [ ] Implement rate limiting on `/login` endpoint
- [ ] Add timing attack mitigation to login

### Important (Should Fix)

- [ ] Increase bcrypt rounds to 14
- [ ] Add security headers (HSTS, X-Content-Type-Options, etc.)
- [ ] Set `DATABASE_ECHO=false` in production
- [ ] Add `.env` to `.dockerignore`
- [ ] Implement refresh tokens

### Nice to Have

- [ ] Add MFA support
- [ ] Implement audit logging
- [ ] Add CAPTCHA to login (prevent bots)
- [ ] Set up vulnerability scanning (Trivy, Snyk)

---

## 📚 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Questions?** Review the code in `src/app/core/security.py` and `src/app/api/deps.py`.
