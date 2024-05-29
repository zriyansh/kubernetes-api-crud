import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: 'http://127.0.0.1:8000' }), 
  endpoints: (builder) => ({
    signUp: builder.mutation({
      query: (user) => ({
        url: '/authen/signup/',
        method: 'POST',
        body: user,
      }),
    }),
    login: builder.mutation({
      query: (credentials) => ({
        url: '/authen/login/',
        method: 'POST',
        body: credentials,
      }),
    }),
    deployApplications: builder.mutation({
      query: () => '/deploy/',
      method: 'POST'
    }),
    fetchApplications: builder.query({
      query: () => '/deploy/deploy-list/',
    }),
    deleteApplication: builder.mutation({
      query: (id) => ({
        url: `/deploy/apps/${id}/`,
        method: 'DELETE',
      }),
    }),
  }),
});

export const {
  useSignUpMutation,
  useLoginMutation,
  useDeployApplicationsMutation,
  useFetchApplicationsQuery,
  useDeleteApplicationMutation,
} = apiSlice;
