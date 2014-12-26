ChangeLog
=========

0.3.2 (unreleased)
------------------

* Add python 3.4 support.

0.3.1 (2014-12-19)
------------------

* ocs_sdk.apis.API accepts the constructor param "user_agent". Defaults to
  "ocs-sdk Pythons/version Platform".
* Check code coverage thanks to coveralls.

0.3.0 (2014-11-12)
------------------

* Add missing license files. Closes #1.
* Create class MetadataAPI to get metadata of a running server.

0.2.1 (2014-10-14)
------------------

* Add documentation.
* Set production URLs as defaults in AccountAPI and ComputeAPI,

0.2.0 (2014-04-16)
------------------

* Added quota methods (has_quota, get_quotas) & their tests, refs: AM-1, AM-11.

0.1.3 (2014-03-07)
------------------

* Minor changes in AccountAPI.perm_matches (67f967d26d3).
* base_url can be given to the constructor of API().
* verify_ssl can be given to the constructor of API().

0.1.2 (2014-02-28)
------------------

* Raise InvalidToken when get_resources is called with and invalid token.

0.1.1 (2014-02-28)
------------------

* Add missing files in source tarball.

0.1.0 (2014-02-28)
------------------

* Initial release.

0.0.0 (2013-06-24)
------------------

* First commit.
