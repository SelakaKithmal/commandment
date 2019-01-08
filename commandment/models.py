# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Jesse Peterson, 2017 Mosen
Licensed under the MIT license. See the included LICENSE.txt file for details.

Attributes:
    db (SQLAlchemy): A reference to flask SQLAlchemy extensions db instance.
"""
from typing import Optional, Type
from flask_sqlalchemy import SQLAlchemy

import datetime
from enum import Enum, IntEnum
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.hybrid import hybrid_property

from .dbtypes import GUID, JSONEncodedDict
from .mdm import CommandStatus, Platform, commands
import base64
from binascii import hexlify
from biplist import Data as NSData
from .profiles.certificates import KeyUsage

db = SQLAlchemy()


class CellularTechnology(IntEnum):
    Nothing = 0
    GSM = 1
    CDMA = 2
    Both = 3


device_tags = db.Table(
    'device_tags',
    db.metadata,
    db.Column('device_id', db.Integer, db.ForeignKey('devices.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
)


class Device(db.Model):
    """An enrolled device.
    
    :table: devices
    """
    __tablename__ = 'devices'

    # Common attributes
    id = db.Column(db.Integer, primary_key=True)
    """id (int):"""
    udid = db.Column(db.String(40), index=True, nullable=True)
    """udid (str): Unique Device Identifier"""
    last_seen = db.Column(db.DateTime, nullable=True)
    """last_seen (datetime.datetime): When the device last contacted the MDM."""
    is_enrolled = db.Column(db.Boolean, default=False)
    """is_enrolled (bool): Whether the MDM should consider this device enrolled."""

    # APNS / Push
    topic = db.Column(db.String, nullable=True)
    """topic (str): The APNS topic the device is listening on."""
    push_magic = db.Column(db.String, nullable=True)
    """push_magic (str): The UUID that establishes a unique relationship between the device and the MDM."""
    # The APNS device token is stored in base64 format. Descriptors are added to handle this encoding and decoding
    # to bytes automatically.
    _token = db.Column(db.String, nullable=True)
    tokenupdate_at = db.Column(db.DateTime)
    # if null there are no outstanding push notifications. If this contains anything then dont attempt to deliver
    # another APNS push.
    last_push_at = db.Column(db.DateTime, nullable=True)
    """last_push_at (datetime.datetime): The datetime when the last push was sent to APNS for this device."""
    last_apns_id = db.Column(db.Integer, nullable=True)
    """last_apns_id (str): The UUID of the last apns command sent."""
    # if the time delta between last_push_at and last_seen is >= several days to a week,
    # this should count as a failed push, and potentially declare the device as dead.
    failed_push_count = db.Column(db.Integer, default=0, nullable=False)

    # Table 5
    last_cloud_backup_date = db.Column(db.DateTime)
    """last_cloud_backup_date (datetime): The date of the last iCloud backup."""
    awaiting_configuration = db.Column(db.Boolean)
    """awaiting_configuration (bool): True if device is waiting at Setup Assistant"""

    # Table 6
    itunes_store_account_is_active = db.Column(db.Boolean)
    """itunes_store_account_is_active (bool): the user is currently logged into an active iTunes Store account."""
    itunes_store_account_hash = db.Column(db.String)
    """itunes_store_account_hash (str): a hash of the iTunes Store account currently logged in."""

    # DeviceInformation : Table 7
    device_name = db.Column(db.String)  # Authenticate
    """device_name (str): Name of the device"""
    os_version = db.Column(db.String)  # Authenticate
    """os_version (str): The operating system version number."""
    build_version = db.Column(db.String)  # Authenticate
    """build_version (str): DeviceInformation BuildVersion"""
    model_name = db.Column(db.String)  # Authenticate
    """model_name (str): Longer name of the hardware model"""
    model = db.Column(db.String)  # Authenticate
    """model (str): Name of the hardware model"""
    product_name = db.Column(db.String)  # Authenticate
    """product_name (str): The base product name of the hardware"""
    serial_number = db.Column(db.String(64), index=True, nullable=True)  # Authenticate
    """serial_number (str): The hardware serial number"""
    device_capacity = db.Column(db.Float, nullable=True)
    """device_capacity (float): total capacity (base 1024 gigabytes)"""
    available_device_capacity = db.Column(db.Float, nullable=True)
    """device_available_capacity (float): available capacity (base 1024 gigabytes)"""
    battery_level = db.Column(db.Float, default=-1.0)
    """battery_level (float): battery level, between 0.0 and 1.0. -1.0 if information is not available."""
    cellular_technology = db.Column(db.Enum(CellularTechnology))
    """cellular_technology (CellularTechnology): cellular technology."""
    imei = db.Column(db.String)
    """imei (str): IMEI number (if device is GSM)."""
    meid = db.Column(db.String)
    """meid (str): MEID number (if device is CSMA)."""
    modem_firmware_version = db.Column(db.String)
    """modem_firmware_version (str): The baseband firmware version."""
    is_supervised = db.Column(db.Boolean)
    """is_supervised (bool): Device is supervised"""
    is_device_locator_service_enabled = db.Column(db.Boolean)
    """is_device_locator_service_enabled (bool): Find My iPhone/Mac enabled."""
    is_activation_lock_enabled = db.Column(db.Boolean)
    """is_activation_lock_enabled (bool): Device has Activation Lock enabled."""
    is_do_not_disturb_in_effect = db.Column(db.Boolean)
    """is_do_not_disturb_in_effect (bool): Device has DND enabled."""
    device_id = db.Column(db.String)  # ATV
    """device_id (str): Device ID (ATV)"""
    eas_device_identifier = db.Column(db.String)
    """eas_device_identifier (str): Exchange ActiveSync Identifier"""
    is_cloud_backup_enabled = db.Column(db.Boolean)
    """is_cloud_backup_enabled (bool): iCloud backup is enabled."""
    local_hostname = db.Column(db.String)
    """local_hostname (str): """
    hostname = db.Column(db.String)
    """hostname (str): """
    sip_enabled = db.Column(db.Boolean)
    """sip_enabled (bool): System Integrity Protection is enabled."""
    # TODO: ActiveManagedUsers
    is_mdm_lost_mode_enabled = db.Column(db.Boolean)
    """is_mdm_lost_mode_enabled (bool): MDM Lost mode is enabled."""
    maximum_resident_users = db.Column(db.Integer)
    """maximum_resident_users (int): Maximum number of users that can use Shared iPad."""

    # OSUpdateSettings : Table 8
    # OSUpdateSettings is flattened
    osu_catalog_url = db.Column(db.String)
    """osu_catalog_url (str): Software Update Catalog URL."""
    osu_is_default_catalog = db.Column(db.Boolean)
    osu_previous_scan_date = db.Column(db.DateTime)
    osu_previous_scan_result = db.Column(db.String)
    osu_perform_periodic_check = db.Column(db.Boolean)
    osu_automatic_check_enabled = db.Column(db.Boolean)
    osu_background_download_enabled = db.Column(db.Boolean)
    osu_automatic_app_installation_enabled = db.Column(db.Boolean)
    osu_automatic_os_installation_enabled = db.Column(db.Boolean)
    osu_automatic_security_updates_enabled = db.Column(db.Boolean)

    # NetworkInfo : Table 9
    iccid = db.Column(db.String)
    """iccid (str): The ICC identifier for the SIM card."""
    bluetooth_mac = db.Column(db.String)
    """bluetooth_mac (str): The bluetooth MAC address"""
    wifi_mac = db.Column(db.String)
    """wifi_mac (str): The WiFi MAC address"""
    # TODO: EthernetMACs
    current_carrier_network = db.Column(db.String)
    """current_carrier_network (str): Name of the current carrier network."""
    sim_carrier_network = db.Column(db.String)
    """sim_carrier_network (str): Name of the home carrier network."""
    subscriber_carrier_network = db.Column(db.String)
    """subscriber_carrier_network (str): Name of the home carrier network (replaces sim_carrier_network)."""
    carrier_settings_version = db.Column(db.String)
    """carrier_settings_version (str): Version of the current carrier settings file."""
    phone_number = db.Column(db.String)
    """phone_number (str): Raw phone number without punctuation."""
    voice_roaming_enabled = db.Column(db.Boolean)
    """voice_roaming_enabled (bool): Voice Roaming is enabled in settings."""
    data_roaming_enabled = db.Column(db.Boolean)
    """data_roaming_enabled (bool): Data Roaming is enabled in settings."""
    is_roaming = db.Column(db.Boolean)
    """is_roaming (bool): The device is currently roaming."""
    personal_hotspot_enabled = db.Column(db.Boolean)
    """personal_hotspot_enabled (bool): Personal HotSpot is currently turned on."""
    subscriber_mcc = db.Column(db.String)
    """subscriber_mcc (str): Home Mobile Country Code (numeric)"""
    subscriber_mnc = db.Column(db.String)
    """subscriber_mnc (str): Home Mobile Network Code (numeric)"""
    current_mcc = db.Column(db.String)
    """current_mcc (str): Current Mobile Country Code (numeric)"""
    current_mnc = db.Column(db.String)
    """current_mnc (str): Current Mobile Network Code (numeric)"""

    # SecurityInfo
    # hardware_encryption_caps = db.Column(DBEnum(HardwareEncryptionCaps))
    passcode_present = db.Column(db.Boolean)
    """passcode_present (bool): Device has a passcode."""
    passcode_compliant = db.Column(db.Boolean)
    """passcode_compliant (bool): The passcode is compliant with all requirements (incl Exchange accounts)."""
    passcode_compliant_with_profiles = db.Column(db.Boolean)
    """passcode_compliant_with_profiles (bool): The passcode is compliant with profile requirements."""
    passcode_lock_grace_period_enforced = db.Column(db.Integer)
    """passcode_lock_grace_period_enforced (int): The current enforced time in seconds before unlock passcode will 
    be required."""
    fde_enabled = db.Column(db.Boolean)
    """fde_enabled (bool): Whether full disk encryption is enabled or not."""
    fde_has_prk = db.Column(db.Boolean)
    """fde_has_prk (bool): Whether FDE has a personal recovery key set."""
    fde_has_irk = db.Column(db.Boolean)
    """fde_has_irk (bool): Whether FDE has an institutional recovery key set."""
    fde_personal_recovery_key_cms = db.Column(db.LargeBinary)  # 10.13
    """fde_personal_recovery_key_cms (bytes): If Escrow is enabled, contains the encrypted PRK"""
    fde_personal_recovery_key_device_key = db.Column(db.String)  # 10.13
    """fde_personal_recovery_key_device_key (str):"""
    firewall_enabled = db.Column(db.Boolean)
    """firewall_enabled (bool): Application firewall is enabled."""
    block_all_incoming = db.Column(db.Boolean)
    """block_all_incoming (bool): All incoming connections are blocked."""
    stealth_mode_enabled = db.Column(db.Boolean)
    """stealth_mode_enabled (bool): Stealth mode is enabled."""

    # ActivationLockBypassCode
    activation_lock_escrow_key = db.Column(db.String)
    """activation_lock_escrow_key (str): The activation lock bypass code generated by the device"""

    # DEP Fetch/Sync Fields
    is_dep = db.Column(db.Boolean)
    """is_dep (bool): This device has been synced from DEP. False indicates a manual or AC2 enrolment"""

    description = db.Column(db.String)
    """description (str): The DEP description which is often identical to the SKU description on the invoice."""
    color = db.Column(db.String)
    """color: (str): The device color indicated by DEP"""
    asset_tag = db.Column(db.String)
    """asset_tag (str): The device asset tag, if provided by Apple."""
    profile_status = db.Column(db.String)
    """profile_status (str): The status of profile installation: empty, assigned, pushed or removed."""
    profile_uuid = db.Column(db.String)
    """profile_uuid (str): The UUID of the assigned DEP profile"""
    profile_assign_time = db.Column(db.DateTime)
    """profile_assign_time (datetime): The date and time indicating when the DEP profile was assigned"""
    profile_push_time = db.Column(db.DateTime)
    """profile_push_time (datetime): The date and time indicating when the DEP profile was pushed."""
    device_assigned_date = db.Column(db.DateTime)
    """device_assigned_date (datetime): The date and time the device was recorded into DEP."""
    device_assigned_by = db.Column(db.String)
    """device_assigned_by (str): The email of the person who assigned the device."""
    os = db.Column(db.String)
    """os (str): The device operating system returned by DEP: iOS, OSX or tvOS"""
    device_family = db.Column(db.String)
    """device_family (str): The device's Apple product family returned by DEP."""

    # TODO: Blocked Applications

    @hybrid_property
    def token(self):
        return self._token if self._token is None else base64.b64decode(self._token)

    @token.setter
    def token(self, value):
        self._token = base64.b64encode(value) if value is not None else None

    @property
    def hex_token(self):
        """Retrieve the device token in hex encoding, necessary for the APNS2 client."""
        if self._token is None:
            return self._token
        else:
            return hexlify(self.token).decode('utf8')

    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'))
    certificate = db.relationship('Certificate', backref='devices')

    dep_profile_id = db.Column(db.Integer, db.ForeignKey('dep_profiles.id'))
    dep_profile = db.relationship('DEPProfile', backref='devices')

    tags = db.relationship(
        'Tag',
        secondary=device_tags,
        back_populates='devices'
    )

    _unlock_token = db.Column(db.String(), name='unlock_token', nullable=True)

    @property
    def unlock_token(self):
        return self._unlock_token

    @unlock_token.setter
    def unlock_token(self, value):
        if isinstance(value, NSData):
            self._unlock_token = NSData.encode('base64')
        else:
            self._unlock_token = value

    @property
    def platform(self) -> Platform:
        if self.model_name in ['iMac', 'MacBook Pro', 'MacBook Air', 'Mac Pro']:  # TODO: obviously not sufficient
            return Platform.macOS
        elif self.model_name in ['iPhone', 'iPad']:
            return Platform.iOS
        else:
            return Platform.Unknown

    def __repr__(self):
        return '<Device ID=%r UDID=%r SerialNo=%r>' % (self.id, self.udid, self.serial_number)


class CommandSequence(db.Model):
    """A command sequence represents a series of commands where all members must succeed in order for the sequence to
    succeed. I.E a single failure or timeout in the sequence stops the delivery of every other member.

    :table: command_sequences
    """
    __tablename__ = 'command_sequences'

    id = db.Column(db.Integer, primary_key=True)


class Command(db.Model):
    """The command model represents a single MDM command that should be, has been, or has failed to be delivered to
    a single enrolled device.
    
    :table: commands
    """
    __tablename__ = 'commands'

    id = db.Column(db.Integer, primary_key=True)
    """id (int): ID"""
    request_type = db.Column(db.String, nullable=False)  # string representation of our local command handler
    """request_type (str): The command RequestType attribute"""
    uuid = db.Column(GUID, index=True, unique=True, nullable=False)
    """uuid (GUID): Globally unique command UUID"""
    parameters = db.Column(MutableDict.as_mutable(JSONEncodedDict),
                           nullable=True)  # JSON add'l data as input to command builder
    """parameters (str): The parameters that were used when generating the command, serialized into JSON. Omitting the
            RequestType and CommandUUID attributes."""
    status = db.Column(db.Enum(CommandStatus), index=True, nullable=False, default=CommandStatus.Queued)
    """status (CommandStatus): The status of the command."""
    queued_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), server_default=db.text('CURRENT_TIMESTAMP'))
    """queued_at (datetime.datetime): The datetime (utc) of when the command was created. Defaults to UTC now"""
    sent_at = db.Column(db.DateTime, nullable=True)
    """sent_at (datetime.datetime): The datetime (utc) of when the command was delivered to the client."""
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    """acknowledged_at (datetime.datetime): The datetime (utc) of when the Acknowledged, Error or NotNow response was
        returned."""
    # command must only be sent after this date
    after = db.Column(db.DateTime, nullable=True)
    """after (datetime.datetime): If not null, the command must not be sent until this datetime is in the past."""

    # number of retries remaining until dead
    ttl = db.Column(db.Integer, nullable=False, default=5)
    """ttl (int): The number of retries remaining until the command will be dead/expired."""

    device_id = db.Column(db.ForeignKey('devices.id'), nullable=True)
    """device_id (int): The device ID on the devices table."""
    device = db.relationship('Device', backref='commands')
    """device (Device): The instance of the related device."""

    # device_user_id = db.Column(ForeignKey('device_users.id'), nullable=True)
    # device_user = relationship('DeviceUser', backref='commands')

    @classmethod
    def from_model(cls, cmd: commands.Command):
        """This method turns a subclass of commands.Command into an SQLAlchemy model.
        The parameters of the command are encoded as a JSON dictionary inside the parameters column.

        Args:
              cmd (commands.Command): The command to be turned into a database model.
        Returns:
              Command: The database model, ready to be committed.
        """
        c = cls()
        assert cmd.request_type is not None
        c.request_type = cmd.request_type
        c.uuid = cmd.uuid
        c.parameters = cmd.parameters

        return c

    @classmethod
    def find_by_uuid(cls, uuid: str):
        """Find and return an instance of the Command model matching the given UUID string.
        
        Args:
              uuid (str): The command UUID
              
        Returns:
              Command: Instance of the command, if any
        """
        return cls.query.filter(cls.uuid == uuid).one()

    @classmethod
    def next_command(cls, device: Device):
        """Get the next available command in the queue for the specified device.

        The next available command must match these predicates:

        - Assigned to this device.
        - The status is "Queued".
        - The `after` field is in the past, or empty.

        Args:
            device (Device): The database model matching the device checking in.

        Returns:
            Command: The next command model to be processed.
        """
        # d == d AND (q_status == Q OR (q_status == R AND result == 'NotNow'))
        return cls.query.filter(db.and_(
            cls.device == device,
            cls.status == CommandStatus.Queued.value)).order_by(cls.id).first()

    @classmethod
    def next(cls, device: Device):  # type: (Type[Command], Device) -> Optional[Command]
        model = cls.query.filter(db.and_(
            cls.device == device,
            cls.status == CommandStatus.Queued.value)).order_by(cls.id).first()


    def __repr__(self):
        return '<Command ID=%r UUID=%r qstatus=%r>' % (self.id, self.uuid, self.status)


class DeviceUser(db.Model):
    """
    This model represents a managed user from the standpoint of the MDM.
    It exists to support the macOS user channel extension.

    :table: device_users
    """
    __tablename__ = 'device_users'

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(db.ForeignKey('devices.id'), nullable=True)
    """(int): Device foreign key ID."""
    device = db.relationship('Device', backref='device_users')
    """(db.relationship): Device relationship"""
    device_udid = db.Column(db.String(40), nullable=False)
    """(GUID): Device UDID"""
    user_id = db.Column(GUID, nullable=False)
    """user_id (GUID): Local user's GUID, or network user's GUID from Directory Record."""
    long_name = db.Column(db.String)
    """long_name (str): The full name of the user"""
    short_name = db.Column(db.String)
    """short_name (str): The short (username) of the user"""
    need_sync_response = db.Column(db.Boolean)  # This is kind of transitive but added anyway.
    user_configuration = db.Column(db.Boolean)
    digest_challenge = db.Column(db.String)
    auth_token = db.Column(db.String)


class Organization(db.Model):
    """The MDM home organization configuration.
    
    These attributes are used as the defaults for several other services where an org name is required.
    Such as Certificate requests and Profile detail.
    
    :table: organizations
    """
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    """id (int): ID"""
    name = db.Column(db.String)
    """name (string): Name"""
    payload_prefix = db.Column(db.String)
    """payload_prefix (string): The reverse-dns style prefix to use for all generated profiles."""

    # http://www.ietf.org/rfc/rfc5280.txt
    # maximum string lengths are well defined by this RFC and this schema follows those recommendations
    # this x.509 name is used in the subject of the internal CA and issued certificates
    x509_ou = db.Column(db.String(32))
    """x509_ou (string): The x.509 Organizational Unit for generating certificates."""
    x509_o = db.Column(db.String(64))
    """x509_o (string): The x.509 Organization for generating certificates."""
    x509_st = db.Column(db.String(128))
    """x509_st (string): The x.509 State for generating certificates."""
    x509_c = db.Column(db.String(2))
    """x509_c (string): The 2 letter x.509 country code for generating certificates. """


class DeviceIdentitySources(Enum):
    """A list of sources for Device Identity."""
    InternalPKCS12 = 'internal_pkcs12'
    InternalSCEP = 'internal_scep'
    ExternalSCEP = 'external_scep'


class SCEPConfig(db.Model):
    """This table holds a single row containing information used to generate the SCEP enrollment profile.
    
    :table: scep_config
    
    See Also:
          - `https://tools.ietf.org/html/rfc3280.html`_.
    """
    __tablename__ = 'scep_config'

    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.Enum(DeviceIdentitySources), default=DeviceIdentitySources.InternalSCEP)
    """source_type (DeviceIdentitySources): Specify the source used for device certificates."""
    url = db.Column(db.String, nullable=False)

    challenge_enabled = db.Column(db.Boolean, default=False)
    challenge = db.Column(db.String)
    ca_fingerprint = db.Column(db.String)
    subject = db.Column(db.String, nullable=False)  # eg. O=x/OU=y/CN=z
    key_size = db.Column(db.Integer, default=2048, nullable=False)
    key_type = db.Column(db.String, default='RSA', nullable=False)
    key_usage = db.Column(db.Enum(KeyUsage), default=KeyUsage.All)

    retries = db.Column(db.Integer, default=3, nullable=False)
    retry_delay = db.Column(db.Integer, default=10, nullable=False)
    certificate_renewal_time_interval = db.Column(db.Integer, default=14, nullable=False)


class SubjectAlternativeNameType(Enum):
    """Types of SubjectAlternativeNames that can be added using cryptography SAN extension.
    
    See Also:
          - `https://tools.ietf.org/html/rfc3280.html`_.
    """

    RFC822Name = 'RFC822Name'
    """E-mail address, see: https://tools.ietf.org/html/rfc822"""

    DNSName = 'DNSName'
    UniformResourceIdentifier = 'UniformResourceIdentifier'
    DirectoryName = 'DirectoryName'
    RegisteredID = 'RegisteredID'
    IPAddress = 'IPAddress'
    OtherName = 'OtherName'
    # TODO: ntPrincipal


class SubjectAlternativeName(db.Model):
    """This table holds SANs included in the SCEP enrollment request.
    
    :table: subject_alternative_names
    """
    __tablename__ = 'subject_alternative_names'

    id = db.Column(db.Integer, primary_key=True)
    discriminator = db.Column(db.Enum(SubjectAlternativeNameType), nullable=False)

    str_value = db.Column(db.String)
    octet_value = db.Column(db.LargeBinary)  # For IPAddress


class Tag(db.Model):
    """This table holds tags, which are categories that are many-to-many and polymorphic to different types of
    objects."""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    color = db.Column(db.String(6), default='888888')

    # applications = db.relationship(
    #     "Application",
    #     secondary=application_tags,
    #     back_populates="tags",
    # )

    devices = db.relationship(
        "Device",
        secondary=device_tags,
        back_populates="tags",
    )

    # profiles = db.relationship(
    #     "Profiles",
    #     secondary=profile_tags,
    #     back_populates="tags",
    # )


