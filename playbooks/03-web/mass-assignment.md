# Mass Assignment

## Before I start
- [ ] Framework that auto-binds (Rails/Laravel/Django/Spring/MVC) — JSON APIs especially

## The play
{"username":"matt","password":"x","isAdmin":true}
{"email":"matt@x.com","role":"admin","balance":999999}
- [ ] Add the field, send, then GET the object / exercise the privilege to verify
- [ ] Field hidden in responses doesn't mean it's not honored

## Find the fields
- [ ] GET responses show fields the form never renders → mirror them back in PUT/PATCH
- [ ] Swagger/docs list writable properties: :Pb api
- [ ] JS bundles carry admin field names
- [ ] Fuzz: isAdmin is_admin admin role group permissions plan verified
- [ ] Framework flavors: user[admin]=1 (Rails), Admin=true (MVC), "is_admin":1 (Laravel)

## Targets
- [ ] Register/profile: role=admin, email_verified=true
- [ ] Order/cart: price=0, discount=100
- [ ] Password change: username=victim
- [ ] Org APIs: tenant_id=1 (cross-tenant, IDOR cousin)

## If it fails
- [ ] Strong params/allow-list → nested JSON {"role":{"name":"admin"}}, arrays ["admin"], content-type confusion (form vs JSON parsers differ)
- [ ] Field rejected everywhere → bug class absent; try server-side parameter pollution instead

## Next
- [ ] Admin → map the admin API surface: :Pb api
- [ ] Business-logic fields → document fraud impact for the report
