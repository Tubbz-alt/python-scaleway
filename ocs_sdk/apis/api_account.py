# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014 Online SAS and Contributors. All Rights Reserved.
#                         Julien Castets <jcastets@ocs.online.net>
#                         Romain Gay <rgay@ocs.online.net>
#                         Kevin Deldycke <kdeldycke@ocs.online.net>
#
# Licensed under the BSD 2-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the
# License at http://opensource.org/licenses/BSD-2-Clause

from six.moves import zip_longest
import slumber

from . import API


class InvalidToken(Exception):
    pass


class ExpiredToken(InvalidToken):
    pass


class BadToken(InvalidToken):
    pass


class AccountAPI(API):
    """ Interacts with OCS Account API.
    """
    base_url = 'https://account.cloud.online.net/'

    def perm_matches(self, request_perm, effective_perm):
        """ Evaluates whether `request_perm` is granted by `effective_perm`.

        Permissions are string separated by semi-colon characters.
        Checking of permissions is performed from left to right and stops at
        the first mismatch between `effective_perm` and `request_perm`.

        The `*` character is used to match all permissions at a given step in
        the permission validation process.

        Examples:
        >>> perm_matches('request:auth:read', 'request:auth:*')
        True
        >>> perm_matches('request:auth:read', 'request:*')
        True
        >>> perm_matches('request:auth:read', 'request:log:*')
        False
        >>> perm_matches('request:log:write', 'request:log:read')
        False

        :param request_perm: Currently granted permissions
        :param effective_perm: Actual permission granted to the token
        """
        if request_perm is None:
            return True

        request_perm_parts = request_perm.split(':')
        effective_perm_parts = effective_perm.split(':')

        for (request_perm_part,
             effective_perm_part) in zip_longest(request_perm_parts,
                                                 effective_perm_parts):

            if (
                request_perm_part != effective_perm_part and
                effective_perm_part != '*' and
                effective_perm_part is not None
            ):
                return False

        return True

    def get_resources(self, service=None, name=None, resource=None):
        """ Gets a list of resources for which the auth token is granted.
        """
        if not self.auth_token:
            return []

        # GET /tokens/:id/permissions on account-api
        try:
            response = self.query().tokens(self.auth_token).permissions.get()

        except slumber.exceptions.HttpClientError as exc:
            if exc.response.status_code == 404:
                raise BadToken()

            if exc.response.status_code == 410:
                raise ExpiredToken()

            raise

        # Apply filters on effective permissions
        #
        # >>> print response.get('permissions')
        # {
        #   'service_name': {
        #      'perm_name': ['resource1', 'resource2', ...],
        #      ...
        #   },
        #   ...
        # }
        ret = []

        for (eff_service_name,
             eff_service_perms) in response.get('permissions', {}).items():

            # Filter on service
            if eff_service_name == service or service is None:

                # Filter on perms
                for (eff_perm_name,
                     eff_perm_resources) in eff_service_perms.items():

                    if self.perm_matches(name, eff_perm_name):

                        # Filter on resources
                        ret.extend([
                            eff_perm_resource
                            for eff_perm_resource in eff_perm_resources
                            if self.perm_matches(resource, eff_perm_resource)
                        ])

        return list(set(ret))

    def has_perm(self, service=None, name=None, resource=None):
        """ Checks if the token has a permission.
        """
        return bool(
            self.get_resources(service=service, name=name, resource=resource)
        )

    def get_quotas(self, organization):
        """ Gets a list of quotas for the given organization.
        """
        response = self.query().organizations(organization).quotas.get()
        return response['quotas']

    def get_quota(self, organization, resource):
        """ Gets one quota for the given organization.
        """
        quotas = self.get_quotas(organization)
        return quotas.get(resource)

    def has_quota(self, organization, resource, used=None):
        """ Checks quota for a resource
        """
        quotas = self.get_quotas(organization=organization)
        return bool(
            resource in quotas and used < quotas.get(resource, 0)
        )
