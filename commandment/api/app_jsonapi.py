"""
    This module contains all of the API generated using the Flask-REST-JSONAPI extension.
"""
from flask import Blueprint
from flask_rest_jsonapi import Api
from .resources import CertificatesList, CertificateDetail, CertificateSigningRequestList, \
    CertificateSigningRequestDetail, PushCertificateList, SSLCertificatesList, \
    CACertificateList, PrivateKeyDetail, DeviceList, DeviceDetail, \
    DeviceRelationship, \
    TagsList, TagDetail, TagRelationship


# PayloadsList, PayloadDetail,

api_app = Blueprint('api_app', __name__)
api = Api(blueprint=api_app)

# Certificates
api.route(CertificatesList, 'certificates_list', '/v1/certificates/')
api.route(CertificateDetail, 'certificate_detail', '/v1/certificates/<int:certificate_id>')

api.route(CertificateSigningRequestList, 'certificate_signing_request_list', '/v1/certificate_signing_requests')
api.route(CertificateSigningRequestDetail, 'certificate_signing_request_detail',
          '/v1/certificate_signing_requests/<int:certificate_signing_request_id>')
api.route(PushCertificateList, 'push_certificates_list', '/v1/push_certificates/')
api.route(SSLCertificatesList, 'ssl_certificates_list', '/v1/ssl_certificates/')
api.route(CACertificateList, 'ca_certificates_list', '/v1/ca_certificates/')
api.route(PrivateKeyDetail, 'private_key_detail', '/v1/rsa_private_keys/<int:private_key_id>')


# Devices
api.route(DeviceList, 'devices_list', '/v1/devices', '/v1/device_groups/<int:device_group_id>/devices',
          '/v1/dep/profiles/<int:dep_profile_id>/devices')
api.route(DeviceDetail, 'device_detail', '/v1/devices/<int:device_id>')
api.route(DeviceRelationship, 'device_commands', '/v1/devices/<int:device_id>/relationships/commands')
api.route(DeviceRelationship, 'device_tags', '/v1/devices/<int:device_id>/relationships/tags')
api.route(DeviceRelationship, 'device_dep_profile', '/v1/devices/<int:device_id>/relationships/dep_profile')

# Organizations
# api.route(OrganizationList, 'organizations_list', '/v1/organizations')
# api.route(OrganizationDetail, 'organization_detail', '/v1/organizations/<int:organization_id>')

# Tags
api.route(TagsList, 'tags_list', '/v1/tags', '/v1/devices/<int:device_id>/tags')
api.route(TagDetail, 'tag_detail', '/v1/tags/<int:tag_id>')
api.route(TagRelationship, 'tag_devices', '/v1/tags/<int:tag_id>/relationships/devices')

