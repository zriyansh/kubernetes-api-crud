import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useLoginMutation, useSignUpMutation } from '../features/api/apiSlice';
import { setCredentials } from '../features/auth/authSlice';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
} from '@chakra-ui/react';

const AuthForm = ({ isLogin }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [login, { isLoading: isLoginLoading }] = useLoginMutation();
  const [signUp, { isLoading: isSignUpLoading }] = useSignUpMutation();
  const dispatch = useDispatch();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const userData = { email, password, username };
      const res = isLogin
        ? await login(userData).unwrap()
        : await signUp(userData).unwrap();
      dispatch(setCredentials({ user: res.user, accessToken: res.accessToken, refreshToken: res.refreshToken }));
    } catch (err) {
      console.error('Failed to authenticate', err);
    }
  };

  return (
    <Box p={8} maxWidth="400px" borderWidth={1} borderRadius={8} boxShadow="lg">
      <Heading mb={6}>{isLogin ? 'Login' : 'Sign Up'}</Heading>
      <form onSubmit={handleSubmit}>
        <VStack spacing={4}>
          {!isLogin && (
            <FormControl id="username">
              <FormLabel>Username</FormLabel>
              <Input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </FormControl>
          )}
          <FormControl id="email">
            <FormLabel>Email</FormLabel>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </FormControl>
          <FormControl id="password">
            <FormLabel>Password</FormLabel>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </FormControl>
          <Button type="submit" colorScheme="teal" isLoading={isLogin ? isLoginLoading : isSignUpLoading}>
            {isLogin ? 'Login' : 'Sign Up'}
          </Button>
        </VStack>
      </form>
    </Box>
  );
};

export default AuthForm;
