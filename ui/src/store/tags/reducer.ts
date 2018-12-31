import {isJSONAPIErrorResponsePayload, JSONAPIDataObject, JSONAPIErrorResponse} from "../../json-api";
import {Tag} from "./types";
import {INDEX_FAILURE, INDEX_REQUEST, INDEX_SUCCESS, IndexActionResponse} from "./actions";

export interface ITagsState {
    loading: boolean;
    items: Array<JSONAPIDataObject<Tag>>;
    error: boolean;
    errorDetail?: JSONAPIErrorResponse;
}

const initialState: ITagsState = {
    error: false,
    items: [],
    loading: false,
};

type TagsAction = IndexActionResponse;

export function tags(state: ITagsState = initialState, action: TagsAction): ITagsState {
    switch (action.type) {
        case INDEX_REQUEST:
            return {
                ...state,
                loading: true,
            };
        case INDEX_SUCCESS:
            if (isJSONAPIErrorResponsePayload(action.payload)) {
                return {
                    ...state,
                    error: true,
                    errorDetail: action.payload,
                }
            } else {
                return {
                    ...state,
                    error: false,
                    items: action.payload.data,
                    loading: false,
                };
            }
        case INDEX_FAILURE:
            return {
                ...state,
                error: true,
                loading: false,
            };
        default:
            return state;
    }
}
