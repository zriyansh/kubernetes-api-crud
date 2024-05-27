import React, { useState } from 'react';
import axios from 'axios';


const SignUp = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');


    const handleSignUp = async () => {
        try {
            await axios.post('http://localhost:8000/authen/signup/', {
                username,
                email,
                password
            });
            alert('Sign-up successful');
        } catch (error) {
            alert('Sign-up failed');
        }
    };

    return (
        <div>
            <h2>Sign Up</h2>
            <input type="text" placeholder="Username" onChange={e => setUsername(e.target.value)} />
            <input type="email" placeholder="Email" onChange={e => setEmail(e.target.value)} />
            <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
            <button onClick={handleSignUp}>Sign Up</button>
            <br />OR<br />
            <br />            
            <button href="/auth/login">Login</button>

        </div>
    );
};

export default SignUp;
