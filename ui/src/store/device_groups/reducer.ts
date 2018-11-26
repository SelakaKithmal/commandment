import {
    INDEX_SUCCESS, IndexActionResponse,
    READ_SUCCESS, ReadActionResponse
} from "./actions";
import {JSONAPIDataObject, isJSONAPIErrorResponsePayload, JSONAPIDetailResponse} from "../../json-api";
import {DeviceGroup} from "./types";
import {Device} from "../device/types";

export interface DeviceGroupsState {
    items?: Array<JSONAPIDataObject<DeviceGroup>>;
    editing?: JSONAPIDetailResponse<DeviceGroup, Device>;
    recordCount: number;
}

const initialState: DeviceGroupsState = {
    items: [],
    recordCount: 0
};

type DeviceGroupsAction = IndexActionResponse | ReadActionResponse;

export function device_groups(state: DeviceGroupsState = initialState, action: DeviceGroupsAction): DeviceGroupsState {
    switch (action.type) {
        case INDEX_SUCCESS:
            if (isJSONAPIErrorResponsePayload(action.payload)) {
                return state;
            } else {
                return {
                    ...state,
                    items: action.payload.data,
                    recordCount: action.payload.meta.count
                };
            }
        case READ_SUCCESS:
            if (isJSONAPIErrorResponsePayload(action.payload)) {
                return state;
            } else {
                return {
                    ...state,
                    editing: action.payload
                };
            }
        default:
            return state;
    }
}
