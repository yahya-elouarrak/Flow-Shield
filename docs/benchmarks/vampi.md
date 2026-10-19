# VAmPI (Vulnerable API) Benchmark

VAmPI is a vulnerable API developed with FastAPI that includes vulnerabilities from the OWASP Top 10 API Security risks. It is a lightweight, single-container application perfect for benchmarking FlowShield's detection capabilities.

## Running VAmPI Locally

VAmPI can be run easily via Docker:

```bash
docker run -d -p 9090:80 --name vampi erev0s/vampi
```

Verify it is running by navigating to:
- Swagger Docs: `http://localhost:9090/docs`
- OpenAPI JSON: `http://localhost:9090/openapi.json`

## FlowShield Project Configuration

To test VAmPI with FlowShield, create a project with the following configuration:

1. **Target API**: `http://host.docker.internal:9090` (assuming FlowShield is running in Docker and VAmPI is on the host on port 9090).
2. **OpenAPI Import URL**: `https://raw.githubusercontent.com/erev0s/VAmPI/master/openapi_specs/openapi3.yml` (or simply import `http://host.docker.internal:9090/openapi.json`).

### Authentication Setup
VAmPI uses JWT tokens for authentication.

- **Login Endpoint**: `POST /users/v1/login`
- **Username Field**: `username`
- **Password Field**: `password`
- **Token Path**: `auth_token` (VAmPI returns `{"auth_token": "..."}`)
- **Header Template**: `Authorization: Bearer {{token}}`

### Test Accounts
You will need to register two users in VAmPI to test BOLA/BFLA effectively. FlowShield requires you to provide credentials for them.
1. **User A**: `user_a` / `password123`
2. **User B**: `user_b` / `password123`

Register them via the VAmPI swagger UI or cURL (`POST /users/v1/register`).

## Benchmarking Goals
FlowShield should be able to detect:
- **BOLA (Broken Object Level Authorization)**: A user accessing another user's data.
- **BFLA (Broken Function Level Authorization)**: A regular user accessing admin endpoints.
- **Mass Assignment**: Modifying fields that shouldn't be modifiable during a request.
