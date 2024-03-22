# Changelog

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
