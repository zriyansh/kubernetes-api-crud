import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import CustomNavbar from './components/Navbar';
import AuthForm from './components/AuthForm';
import ApplicationTable from './components/ApplicationTable';

function App() {
  return (
    <Router>
      <CustomNavbar />
      <Routes>
        <Route path="/login" element={<AuthForm isLogin />} />
        <Route path="/signup" element={<AuthForm />} />
        <Route path="/applications" element={<ApplicationTable />} />
      </Routes>
    </Router>
  );
}

export default App;
