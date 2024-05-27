import { createSlice } from '@reduxjs/toolkit';

const applicationSlice = createSlice({
  name: 'application',
  initialState: {
    applications: [],
  },
  reducers: {
    setApplications: (state, { payload }) => {
      state.applications = payload;
    },
  },
});

export const { setApplications } = applicationSlice.actions;
export default applicationSlice.reducer;
