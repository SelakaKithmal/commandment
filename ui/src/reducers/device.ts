import * as actions from '../actions/devices';
import {
    CommandsActionResponse, PatchRelationshipActionResponse, PostRelatedActionResponse,
    ReadActionResponse
} from "../actions/devices";
import {CertificatesActionResponse} from '../actions/device/certificates';
import {commands, DeviceCommandsState} from "./device/commands";
import {installed_certificates, InstalledCertificatesState} from "./device/installed_certificates";
import {installed_applications, InstalledApplicationsState} from "./device/installed_applications";
import {InstalledApplicationsActionResponse} from "../actions/device/applications";
import {installed_profiles, InstalledProfilesState} from "./device/installed_profiles";
import {JSONAPIDataObject, isJSONAPIErrorResponsePayload} from "../json-api";
import {Device, Tag} from "../models";
import {available_os_updates, AvailableOSUpdatesState} from "./device/available_os_updates";
import {isArray} from "../guards";
import {DevicesActionTypes} from "../actions/devices";


export interface DeviceState {
    device?: JSONAPIDataObject<Device>;
    loading: boolean;
    error: boolean;
    errorDetail?: any
    lastReceived?: Date;
    currentPage: number;
    pageSize: number;
    recordCount?: number;
    commands?: DeviceCommandsState;
    installed_certificates?: InstalledCertificatesState;
    installed_applications?: InstalledApplicationsState;
    installed_profiles?: InstalledProfilesState;
    available_os_updates?: AvailableOSUpdatesState;
    tags?: Array<JSONAPIDataObject<Tag>>;
    tagsLoading: boolean;
}

const initialState: DeviceState = {
    device: null,
    loading: false,
    tagsLoading: false,
    error: false,
    errorDetail: null,
    lastReceived: null,
    currentPage: 1,
    pageSize: 50
};

type DevicesAction = ReadActionResponse | InstalledApplicationsActionResponse | CommandsActionResponse |
    CertificatesActionResponse | PatchRelationshipActionResponse | PostRelatedActionResponse;

export function device(state: DeviceState = initialState, action: DevicesAction): DeviceState {
    switch (action.type) {
        case DevicesActionTypes.READ_REQUEST:
            return {
                ...state,
                loading: true
            };

        case DevicesActionTypes.READ_FAILURE:
            return {
                ...state,
                error: true,
                errorDetail: action.payload
            };

        case DevicesActionTypes.READ_SUCCESS:
            if (isJSONAPIErrorResponsePayload(action.payload)) {
                return {
                    ...state,
                    error: true,
                    errorDetail: action.payload
                }
            } else {
                let tags: Array<JSONAPIDataObject<Tag>> = [];

                if (action.payload.included) {
                    tags = action.payload.included.filter((included: JSONAPIDataObject<any>) => (included.type === 'tags'));
                }

                return {
                    ...state,
                    device: action.payload.data,
                    lastReceived: new Date,
                    loading: false,
                    tags
                };
            }
        case actions.RPATCH_REQUEST:
            return {
                ...state,
                tagsLoading: true
            };
        case actions.RPATCH_SUCCESS:
            if (isJSONAPIErrorResponsePayload(action.payload)) {
                return {
                    ...state,
                    error: true,
                    errorDetail: action.payload
                }
            } else {
                const device: JSONAPIDataObject<Device> = {
                    ...state.device,
                    relationships: {
                        ...state.device.relationships,
                        tags: action.payload.data.relationships.tags
                    }
                };

                return {
                    ...state,
                    device,
                    tagsLoading: false
                };
            }

        case actions.RPATCH_FAILURE:
            return {
                ...state,
                tagsLoading: false
            };

        case actions.RCPOST_REQUEST:
            return {
                ...state,
                tagsLoading: true
            };

        case actions.RCPOST_SUCCESS:
            const data: Array<any> = isArray(action.payload.data) ? action.payload.data : [action.payload.data];
            const mergedTags = data.concat(state.device.relationships.tags.data);

            return {
                ...state,
                device: {
                    ...state.device,
                    relationships: {
                        ...state.device.relationships,
                        tags: {
                            data: mergedTags
                        }
                    }
                }
            };

        case actions.RCPOST_FAILURE:
            return {
                ...state,
                tagsLoading: false,
                error: true,
                errorDetail: action.payload
            };
            
        default:
            return {
                ...state,
                commands: commands(state.commands, action),
                installed_certificates: installed_certificates(state.installed_certificates, action),
                installed_applications: installed_applications(state.installed_applications, action),
                installed_profiles: installed_profiles(state.installed_profiles, action),
                available_os_updates: available_os_updates(state.available_os_updates, action)
            };
    }
}