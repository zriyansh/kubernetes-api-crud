import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Box, Flex, Link, Button, Heading } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { clearCredentials } from '../features/auth/authSlice';

const CustomNavbar = () => {
  const { user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();

  const handleLogout = () => {
    dispatch(clearCredentials());
    window.location.href = '/';
  };

  return (
    <Box bg="teal.500" px={4}>
      <Flex h={16} alignItems="center" justifyContent="space-between">
        <Heading size="md" color="white">MyApp</Heading>
        <Flex alignItems="center">
          {user ? (
            <>
              <Link as={RouterLink} to="/applications" px={2} color="white">Applications</Link>
              <Button onClick={handleLogout} px={2} colorScheme="teal">Logout</Button>
            </>
          ) : (
            <>
              <Link as={RouterLink} to="/login" px={2} color="white">Login</Link>
              <Link as={RouterLink} to="/signup" px={2} color="white">Sign Up</Link>
            </>
          )}
        </Flex>
      </Flex>
    </Box>
  );
};

export default CustomNavbar;
