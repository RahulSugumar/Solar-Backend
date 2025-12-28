
### API Endpoints (Final MVP Set)

#### Auth
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`

#### Public
- `GET /map/solar-sites`
- `GET /stats/platform`
- `GET /lands/available`

#### Land Owner
- `POST /land/submit` (Fields: Title, Location, Type, Ownership, Area, Photos)
- `GET /land/my-lands`
- `GET /land/my-earnings`
- `GET /land/map`

#### Investor
- `GET /invest/available-lands?location={query}`
- `GET /invest/land/{id}` (Includes: Capacity, Price, Returns)
- `POST /invest/request` (Reserves land)
- `GET /invest/my-requests`
- `GET /invest/my-investments`
- `GET /invest/notifications`

#### Payment & Admin
- `POST /payment/mark-paid`
- `GET /admin/investor-requests`
- `GET /admin/land-requests`
- `POST /admin/investor-approve` (Can set final amount)
- `POST /admin/land-approve`
