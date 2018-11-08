import * as React from 'react';
import {ModelIcon} from "../ModelIcon";
import {Link} from 'react-router-dom';
import {Device} from "../../models";
import {JSONAPIDataObject} from "../../json-api";


interface DeviceColumnProps {
    rowData: JSONAPIDataObject<Device>;
}

export class DeviceColumn extends React.Component<DeviceColumnProps, undefined> {
    render () {
        const {
            rowData
        } = this.props;

        return (
            <div>
                <Link to={`/devices/${rowData.id}`}>
                    <span>{ rowData.attributes.device_name ? rowData.attributes.device_name : `DEP ${rowData.attributes.description}`  }</span>
                </Link>
            </div>
        )
    }
}