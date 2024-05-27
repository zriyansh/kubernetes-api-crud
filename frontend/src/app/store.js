import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import applicationReducer from '../features/application/applicationSlice';
import { apiSlice } from '../features/api/apiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    application: applicationReducer,
    [apiSlice.reducerPath]: apiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(apiSlice.middleware),
});
