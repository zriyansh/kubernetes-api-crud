import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: 'http://localhost:3000/authen' }),
  endpoints: (builder) => ({
    signUp: builder.mutation({
      query: (user) => ({
        url: '/signup',
        method: 'POST',
        body: user,
      }),
    }),
    login: builder.mutation({
      query: (credentials) => ({
        url: '/login',
        method: 'POST',
        body: credentials,
      }),
    }),
    fetchApplications: builder.query({
      query: () => '/applications',
    }),
    deleteApplication: builder.mutation({
      query: (id) => ({
        url: `/applications/${id}`,
        method: 'DELETE',
      }),
    }),
  }),
});

export const {
  useSignUpMutation,
  useLoginMutation,
  useFetchApplicationsQuery,
  useDeleteApplicationMutation,
} = apiSlice;
