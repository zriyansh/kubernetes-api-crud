import React from 'react';
import { Box, Flex, Link, Button, Heading } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const CustomNavbar = () => {
  return (
    <Box bg="teal.500" px={4}>
      <Flex h={16} alignItems="center" justifyContent="space-between">
        <Heading size="md" color="white">MyApp</Heading>
        <Flex alignItems="center">
          <Link as={RouterLink} to="/login" px={2} color="white">Login</Link>
          <Link as={RouterLink} to="/signup" px={2} color="white">Sign Up</Link>
          <Link as={RouterLink} to="/applications" px={2} color="white">Applications</Link>
        </Flex>
      </Flex>
    </Box>
  );
};

export default CustomNavbar;
