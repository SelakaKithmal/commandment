import * as React from "react";
import {connect, MapStateToProps} from "react-redux";
import {Dispatch} from "redux";
import Container from "semantic-ui-react/src/elements/Container";
import Header from "semantic-ui-react/src/elements/Header";
import {RouteComponentProps} from "react-router";
import {bindActionCreators} from "redux";
import {IDEPAccountsState} from "../../store/dep/accounts_reducer";
import {RootState} from "../../reducers/index";
import {DEPAccountsTable} from "../../components/react-tables/DEPAccountsTable";
import Dropdown from "semantic-ui-react/dist/commonjs/modules/Dropdown/Dropdown";
import {Link} from "react-router-dom";
import Grid from "semantic-ui-react/dist/commonjs/collections/Grid/Grid";
import {
    AccountIndexActionCreator, accounts,
} from "../../store/dep/actions";
import Icon from "semantic-ui-react/dist/commonjs/elements/Icon/Icon";
import Button from "semantic-ui-react/dist/commonjs/elements/Button/Button";
import Divider from "semantic-ui-react/dist/commonjs/elements/Divider/Divider";
import Breadcrumb from "semantic-ui-react/dist/commonjs/collections/Breadcrumb/Breadcrumb";

interface RouteProps {

}

interface ReduxStateProps {
    accounts: IDEPAccountsState;
}

interface ReduxDispatchProps {
    getAccounts: AccountIndexActionCreator;
}

interface OwnProps extends ReduxStateProps, ReduxDispatchProps, RouteComponentProps<RouteProps> {

}

export class UnconnectedDEPAccountsPage extends React.Component<OwnProps, void> {

    public componentWillMount?() {
        this.props.getAccounts();
    }


    public render() {
        const {
            accounts,
        } = this.props;

        return (
            <Container className="DEPAccountsPage">
                <Divider hidden />
                <Breadcrumb>
                    <Breadcrumb.Section><Link to={`/`}>Home</Link></Breadcrumb.Section>
                    <Breadcrumb.Divider />
                    <Breadcrumb.Section><Link to={`/settings`}>Settings</Link></Breadcrumb.Section>
                    <Breadcrumb.Divider />
                    <Breadcrumb.Section active>DEP Accounts</Breadcrumb.Section>
                </Breadcrumb>

                <Header as="h1">DEP Accounts</Header>
                <Grid>
                    <Grid.Column>
                        <Button icon labelPosition='left' as={Link} to="/settings/dep/accounts/add">
                            <Icon name='plus' />
                            New
                        </Button>
                    </Grid.Column>
                </Grid>
                <Grid>
                    <Grid.Column>
                        <DEPAccountsTable data={accounts.data}
                                          loading={accounts.loading} />
                    </Grid.Column>
                </Grid>
            </Container>
        );
    }
}

export const DEPAccountsPage = connect<ReduxStateProps, ReduxDispatchProps>(
    (state: RootState): ReduxStateProps => ({
        accounts: state.dep.accounts,
    }),
    (dispatch: Dispatch) => bindActionCreators({
        getAccounts: accounts,
    }, dispatch),
)(UnconnectedDEPAccountsPage);
