# Changelog

## [2.2.0](https://github.com/derlin/mantelo/compare/v2.1.1...v2.2.0) (2024-12-29)

**IMPORTANT**: This release removes the `slumber` dependency and integrates its functionality
directly into Mantelo. Unless you directly used `slumber` in your code, this change should not
affect you.

### 🚀 Features

* raise more granular HttpException (HttpNotFound, HttpClientError, HttpServerError) ([33588c8](https://github.com/derlin/mantelo/commit/33588c8b1e3b4962706fc636fc791533b5e8a8ed))
* remove dependency on Slumber and integrate its functionality into Mantelo ([33588c8](https://github.com/derlin/mantelo/commit/33588c8b1e3b4962706fc636fc791533b5e8a8ed))
* return an empty string (versus b'' or None) when the body is empty ([33588c8](https://github.com/derlin/mantelo/commit/33588c8b1e3b4962706fc636fc791533b5e8a8ed))


### 🐛 Bug Fixes

* add missing type annotations ([31d52d3](https://github.com/derlin/mantelo/commit/31d52d39abc954c21d22e06f3483673161586405))
* allow DELETE to have a body ([4cab8aa](https://github.com/derlin/mantelo/commit/4cab8aa1c0aa02d4442ae196ea9691de943f4bc8))
* make HttpException handle responses with non-empty, non-JSON body ([33588c8](https://github.com/derlin/mantelo/commit/33588c8b1e3b4962706fc636fc791533b5e8a8ed))


### 💬 Documentation

* document "as_raw" to get the raw response ([33588c8](https://github.com/derlin/mantelo/commit/33588c8b1e3b4962706fc636fc791533b5e8a8ed))
* document dashes and .url ([13852f1](https://github.com/derlin/mantelo/commit/13852f1c2d46d523a5f83574bb68cfd859504a6d))

## [2.1.1](https://github.com/derlin/mantelo/compare/v2.1.0...v2.1.1) (2024-11-16)


### 🐛 Bug Fixes

* make HttpException handle response with no body properly ([ea4d4b7](https://github.com/derlin/mantelo/commit/ea4d4b7edbf724075c4d4257036ecdb0967cf9d4))
* unset ADMIN variables ([5bf2263](https://github.com/derlin/mantelo/commit/5bf226327337c09e58368ffba1b720cac6dc5ea8))


### 💬 Documentation

* add a FAQ page in readthedocs ([88ba664](https://github.com/derlin/mantelo/commit/88ba664b41e26fc85f879bfd852ada95565ae238))


### 🦀 Build and CI

* avoid duplicate runs ([838d64c](https://github.com/derlin/mantelo/commit/838d64cd9143f30a106f9aa0599c84f326631ffe))

## [2.1.0](https://github.com/derlin/mantelo/compare/v2.0.0...v2.1.0) (2024-07-28)


### 🚀 Features

* add realms property ([84da9e7](https://github.com/derlin/mantelo/commit/84da9e749cc76b194a1c72ea60753665606600f7))


### 🐛 Bug Fixes

* add response object to AuthenticationException ([feccdeb](https://github.com/derlin/mantelo/commit/feccdeb9773280a4cb8802ec3e280b7b185764ef))
* make it possible to query the current realm ([67c2b45](https://github.com/derlin/mantelo/commit/67c2b45bc423d238f08a4d808a1cd99d437aa952))


### 💬 Documentation

* add more examples ([b801ade](https://github.com/derlin/mantelo/commit/b801ade831569f396f17f265110c3b7abcada31f))
* add opengraph meta ([0310e41](https://github.com/derlin/mantelo/commit/0310e41f87b18f844ba4a140ddc944dfb484baf2))
* add readthedocs documentation ([04cc4d7](https://github.com/derlin/mantelo/commit/04cc4d70f3baf91050d4eecda2889b381944b820))
* fix an rst link ([a7ae889](https://github.com/derlin/mantelo/commit/a7ae889611f7a31f2af7120423711c04c535e5b2))


### 🦀 Build and CI

* fix failing healthcheck after keycloak update ([890f416](https://github.com/derlin/mantelo/commit/890f41686717809331c1c3b5f6123f5ab4261b5d))
* fix weekly build ([783aad4](https://github.com/derlin/mantelo/commit/783aad46a9632fe139dd820bfcd1f55a45986250))
* run tests weekly ([bbbc54d](https://github.com/derlin/mantelo/commit/bbbc54d9bc7eba84a440836a7e38cb18c7e572a6))

## [2.0.0](https://github.com/derlin/mantelo/compare/v1.0.1...v2.0.0) (2024-03-21)


### ⚠ BREAKING CHANGES

* rename "ServiceAccount" to "ClientCredentials" and KeycloakAdmin class methods
* drop custom headers support and share session between auth and client

### 🚀 Features

* add the possibility to switch realms ([a6a775a](https://github.com/derlin/mantelo/commit/a6a775a55270ef1c3855772922f6e2394621647f))
* drop custom headers support and share session between auth and client ([32e1254](https://github.com/derlin/mantelo/commit/32e1254a7032fa2d5a4146e0adb9649c9445bddb))
* make session, base_url and realm_name available on the client ([cfdc0b5](https://github.com/derlin/mantelo/commit/cfdc0b51b60d3e741743dcbfd24bac85beddd987))
* rename "ServiceAccount" to "ClientCredentials" and KeycloakAdmin class methods ([df55100](https://github.com/derlin/mantelo/commit/df55100982a2391c2c2b1ba6a1986b02775f98f5))

## [1.0.1](https://github.com/derlin/mantelo/compare/v1.0.0...v1.0.1) (2024-03-21)


### 🐛 Bug Fixes

* add author and version information to package ([33603fb](https://github.com/derlin/mantelo/commit/33603fb1f88a64beebec77e32b4774c2a585c897))
* add py.typed file ([fc371da](https://github.com/derlin/mantelo/commit/fc371da3f27ba9cbc8d74a3891050d4ee84c49a8))
* make BearerAuth's token_getter public ([b94f33c](https://github.com/derlin/mantelo/commit/b94f33cd26a489265fc741f18c6d9fd3cedb4e7a))


### 💬 Documentation

* create a CONTRIBUTING guide ([fb29ebb](https://github.com/derlin/mantelo/commit/fb29ebb1844156595c043a62bc334fce16b20932))

## 1.0.0 (2024-03-18)


### 🚀 Features

* add first implementation ([0c8a8cd](https://github.com/derlin/mantelo/commit/0c8a8cd9069cd5e19272184d5cf120b5b95fb245))
* check typing with mypy ([5a69c35](https://github.com/derlin/mantelo/commit/5a69c35942f0ac86a8192e6ba4c51188dfd7b86f))


### 💬 Documentation

* add Makefile help ([609aaba](https://github.com/derlin/mantelo/commit/609aaba37ab7e57b526b4d444f85249aed8d95ff))
* add README ([fbfd30d](https://github.com/derlin/mantelo/commit/fbfd30ddcad61318585c0d3e59db5d52a175a2a6))


### 🦀 Build and CI

* add build workflow ([9fa358b](https://github.com/derlin/mantelo/commit/9fa358b424e926b5de66ec4823c94ccf1b72fc1f))
* add release process ([7560451](https://github.com/derlin/mantelo/commit/7560451d3354d86d1ed3fde70cf444c25424ac2c))
* upload to codecov ([600381b](https://github.com/derlin/mantelo/commit/600381b181a352fd495789fa4832769cc1446b04))
