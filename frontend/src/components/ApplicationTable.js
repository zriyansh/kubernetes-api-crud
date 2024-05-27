import React from 'react';
import { useFetchApplicationsQuery, useDeleteApplicationMutation } from '../features/api/apiSlice';
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Box,
  Button,
  Spinner,
  Center,
} from '@chakra-ui/react';

const ApplicationTable = () => {
  const { data: applications, isLoading, isError } = useFetchApplicationsQuery();
  const [deleteApplication] = useDeleteApplicationMutation();

  if (isLoading) {
    return <Center><Spinner /></Center>;
  }

  if (isError) {
    return <Center>Error loading applications</Center>;
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this application?')) {
      await deleteApplication(id);
    }
  };

  return (
    <Box p={4}>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Application Name</Th>
            <Th>Namespace</Th>
            <Th>Deployed At</Th>
            <Th>Status</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {applications.map((app) => (
            <Tr key={app.id}>
              <Td>{app.name}</Td>
              <Td>{app.namespace}</Td>
              <Td>{app.deployed_at}</Td>
              <Td>{app.status}</Td>
              <Td>
                <Button colorScheme="red" onClick={() => handleDelete(app.id)}>
                  Delete
                </Button>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default ApplicationTable;
