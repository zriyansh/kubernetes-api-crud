import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { ChakraProvider } from '@chakra-ui/react';
import { store } from './app/store';
import App from './App';

ReactDOM.render(
  <Provider store={store}>
    <ChakraProvider>
      <App />
    </ChakraProvider>
  </Provider>,
  document.getElementById('root')
);
