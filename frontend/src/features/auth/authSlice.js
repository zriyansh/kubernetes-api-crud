import { createSlice } from '@reduxjs/toolkit';

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    accessToken: null,
    refreshToken: null,
  },
  reducers: {
    setCredentials: (state, { payload }) => {
      state.user = payload.user;
      state.accessToken = payload.accessToken;
      state.refreshToken = payload.refreshToken;
    },
    logOut: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
    },
  },
});

export const { setCredentials, logOut } = authSlice.actions;
export default authSlice.reducer;
