import * as React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, compose, createStore} from 'redux';
import {addDecorator, Story, StoryDecorator} from '@storybook/react';

const composeEnhancers = (window as any).__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

const store = createStore((state, action) => state, composeEnhancers());

const StoreDecorator: StoryDecorator = (story) => (
    <Provider store={store}>
        { story() }
    </Provider>
);

addDecorator(StoreDecorator);
