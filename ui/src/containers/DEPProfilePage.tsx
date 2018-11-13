import * as React from "react";

import {connect, Dispatch} from "react-redux";
import {RouteComponentProps} from "react-router";
import {bindActionCreators} from "redux";
import {AccordionTitleProps, FormProps} from "semantic-ui-react";
import Breadcrumb from "semantic-ui-react/dist/commonjs/collections/Breadcrumb/Breadcrumb";
import Message from "semantic-ui-react/dist/commonjs/collections/Message/Message";
import Container from "semantic-ui-react/dist/commonjs/elements/Container/Container";
import Header from "semantic-ui-react/dist/commonjs/elements/Header/Header";
import {DEPProfileForm, IDEPProfileFormValues} from "../components/forms/DEPProfileForm";
import {RSAAApiErrorMessage} from "../components/RSAAApiErrorMessage";
import {RootState} from "../reducers";
import {postProfile, profile, ProfilePostActionRequest, ProfileReadActionRequest} from "../store/dep/actions";
import {IDEPProfileState} from "../store/dep/profile_reducer";
import {DEPProfile, SkipSetupSteps} from "../store/dep/types";

interface IReduxStateProps {
    dep_profile?: IDEPProfileState;
}

interface IReduxDispatchProps {
    getDEPProfile: ProfileReadActionRequest;
    postDEPProfile: ProfilePostActionRequest;
}

interface IRouteParameters {
    account_id: string;
    id?: string;
}

interface IDEPProfilePageProps extends IReduxStateProps, IReduxDispatchProps, RouteComponentProps<IRouteParameters> {

}

interface IDEPProfilePageState {
    activeIndex: string | number;
}

class UnconnectedDEPProfilePage extends React.Component<IDEPProfilePageProps, IDEPProfilePageState> {

    constructor(props: IDEPProfilePageProps) {
        super(props);
        this.state = {
            activeIndex: 0,
        };
    }

    public componentWillMount() {
        const {
            match: {
                params: {
                    id,
                },
            },
        } = this.props;

        if (id) {
            this.props.getDEPProfile(this.props.match.params.id);
        }
    }

    public render() {
        const {
            dep_profile,
            match: {
                params: {
                    id,
                },
            },
        } = this.props;

        let title = "loading";
        if (id) {
            title = `Edit ${this.props.dep_profile.dep_profile ?
                this.props.dep_profile.dep_profile.attributes.profile_name : "Loading..."}`;
        } else {
            title = "Create a new DEP Profile";
        }

        return (
            <Container className="DEPProfilePage">
                <Breadcrumb>
                    <Breadcrumb.Section link>Home</Breadcrumb.Section>
                    <Breadcrumb.Divider />
                    <Breadcrumb.Section link>DEP Account</Breadcrumb.Section>
                    <Breadcrumb.Divider />
                    <Breadcrumb.Section active>DEP Profile</Breadcrumb.Section>
                </Breadcrumb>

                <Header as="h1">{title}</Header>
                {dep_profile.error && <RSAAApiErrorMessage error={dep_profile.errorDetail} />}
                <DEPProfileForm onSubmit={this.handleSubmit}
                                loading={dep_profile.loading}
                                data={dep_profile.dep_profile && dep_profile.dep_profile.attributes}
                                id={dep_profile.dep_profile && dep_profile.dep_profile.id}
                                activeIndex={this.state.activeIndex}
                                onClickAccordionTitle={this.handleAccordionClick}
                />
            </Container>
        );
    }

    private handleSubmit = (values: IDEPProfileFormValues) => {
        const { show, ...profile } = values;
        profile.skip_setup_items = [];

        if (show) {
            for (const kskip in SkipSetupSteps) {
                if (!show[kskip]) {
                    profile.skip_setup_items.unshift(kskip as SkipSetupSteps);
                }
            }
        }

        profile.url = "http://test.something/dep/enroll"; // TODO: THIS IS A PLACEHOLDER

        this.props.postDEPProfile(profile, {
            dep_account: { type: "dep_accounts", id: this.props.match.params.account_id } });
    };

    private handleAccordionClick = (event: React.MouseEvent<any>, data: AccordionTitleProps) => {
        this.setState({ activeIndex: data.index });
    };
}

export const DEPProfilePage = connect(
    (state: RootState, ownProps: any): IReduxStateProps => {
        return {dep_profile: state.dep.profile};
    },
    (dispatch: Dispatch<RootState>, ownProps?: any): IReduxDispatchProps => bindActionCreators({
        getDEPProfile: profile,
        postDEPProfile: postProfile,
    }, dispatch),
)(UnconnectedDEPProfilePage);