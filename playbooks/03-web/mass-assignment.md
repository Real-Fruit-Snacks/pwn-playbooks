# Mass assignment

## Before I start
- [ ] A framework that binds request fields to objects by itself, such as Rails, Laravel, Django, Spring or ASP.NET MVC, above all behind a JSON API

## The move
An extra field in the JSON body of a registration or profile request, with THE-EMAIL my own address:
{"username":"<Username>","password":"<Password>","isAdmin":true}
{"email":"THE-EMAIL","role":"admin","balance":999999}
- [ ] The field added and sent, then the object read back or the privilege used, to see whether it took
- [ ] A field that responses leave out may still be accepted

## Find the fields
- [ ] Fields in GET responses that the form never shows: sent back in PUT or PATCH
- [ ] Writable properties listed in Swagger or other API documentation: :Pb api
- [ ] Administrator field names in the JavaScript bundles
- [ ] Names to guess: isAdmin, is_admin, admin, role, group, permissions, plan, verified
- [ ] By framework: user[admin]=1 in Rails, Admin=true in ASP.NET MVC, "is_admin":1 in Laravel

## Targets
- [ ] Registration and profile: role=admin, email_verified=true
- [ ] Orders and carts: price=0, discount=100
- [ ] A password change: username set to another user's
- [ ] Multi-tenant APIs: tenant_id=1, for another tenant's data, close to :Pb idor

## If it fails
- [ ] Strong parameters or an allow list: nested JSON, {"role":{"name":"admin"}}, an array, ["admin"], and the other content type, since form and JSON parsers differ
- [ ] The field rejected everywhere: not here, so server-side parameter pollution instead

## Next
- [ ] Administrator: the administrator API mapped, :Pb api
- [ ] Price and balance fields: what they would cost the business, written up
