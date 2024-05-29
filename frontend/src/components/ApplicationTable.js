import React, { useState, useEffect } from 'react';
import {
  useFetchApplicationsQuery,
  useDeleteApplicationMutation,
} from '../features/api/apiSlice';
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
  Text,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Container,
} from '@chakra-ui/react';
import axios from 'axios';

const ApplicationTable = () => {
  const { data: applications, isLoading, isError, error, refetch } = useFetchApplicationsQuery();
  const [deleteApplication] = useDeleteApplicationMutation();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedApp, setSelectedApp] = useState(null);
  const [statusUpdates, setStatusUpdates] = useState({});
  const [namespace, setNamespace] = useState('');
  const [applicationName, setApplicationName] = useState('');
  const [chartLink, setChartLink] = useState('');
  const [formError, setFormError] = useState('');

  useEffect(() => {
    const socket = new WebSocket('ws://127.0.0.1:8000/ws/deployments/');

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStatusUpdates((prev) => ({
        ...prev,
        [data.application_id]: data.status,
      }));
    };

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    refetch();
  }, [statusUpdates, refetch]);

  if (isLoading) {
    return (
      <Center>
        <Spinner />
      </Center>
    );
  }

  if (isError) {
    console.error('Error fetching applications:', error);
    return (
      <Center>
        <Text>Error loading applications</Text>
      </Center>
    );
  }

  const handleDelete = async () => {
    if (selectedApp) {
      try {
        await deleteApplication(selectedApp.id).unwrap();
        window.location.reload(); 
      } catch (err) {
        console.error('Failed to delete the application:', err);
      } finally {
        setSelectedApp(null);
        onClose();
      }
    }
  };

  const handleDeploy = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/deploy/', {
        namespace: namespace,
        application_name: applicationName,
        chart_link: chartLink,
      });

      setNamespace('');
      setApplicationName('');
      setChartLink('');
      setFormError('');

      refetch();
    } catch (error) {
      if (error.response && error.response.data) {
        setFormError(error.response.data.error);
      } else {
        setFormError('An unexpected error occurred.');
      }
    }
  };

  return (
    <Box p={9}>
      <VStack spacing={4} mb={6}>
      <Container maxW='550px'>
        <FormControl id="namespace">
          <FormLabel my={1}>Namespace (unique)</FormLabel>
          <Input
            type="text"
            value={namespace}
            onChange={(e) => setNamespace(e.target.value)}
          />
        </FormControl>
        <FormControl id="applicationName">
          <FormLabel my={1}>Application Name</FormLabel>
          <Input
            type="text"
            value={applicationName}
            onChange={(e) => setApplicationName(e.target.value)}
          />
        </FormControl>
        <FormControl id="chartLink">
          <FormLabel my={1}>Chart Link</FormLabel>
          <Input
            type="text"
            value={chartLink}
            onChange={(e) => setChartLink(e.target.value)}
          />
        </FormControl>
        {formError && (
          <Text color="red.500">{formError}</Text>
        )}
        <Button colorScheme="teal" my={3} onClick={handleDeploy}>
          Deploy
        </Button>
        </Container>
      </VStack>
      
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Id</Th>
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
              <Td>{app.id}</Td>
              <Td>{app.application_name}</Td>
              <Td>{app.namespace}</Td>
              <Td>{new Date(app.deployed_at).toLocaleString()}</Td>
              <Td>{statusUpdates[app.id] || app.status}</Td>
              <Td>
                <Button
                  colorScheme="red"
                  onClick={() => {
                    setSelectedApp(app);
                    onOpen();
                  }}
                >
                  Delete
                </Button>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Confirm Deletion</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            Are you sure you want to delete the application{' '}
            <strong>{selectedApp?.application_name}</strong>?
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="red" onClick={handleDelete} ml={3}>
              Delete
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default ApplicationTable;
