import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Applications = () => {
    const [applications, setApplications] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            const result = await axios('/deploy/');
            setApplications(result.data);
        };

        fetchData();
    }, []);

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this application?')) {
            await axios.delete(`/deploy/${id}/`);
            setApplications(applications.filter(app => app.id !== id));
        }
    };

    return (
        <div>
            <h2>Applications</h2>
            <table>
                <thead>
                    <tr>
                        <th>Application Name</th>
                        <th>Namespace</th>
                        <th>Deployed At</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {applications.map(app => (
                        <tr key={app.id}>
                            <td>{app.app_name}</td>
                            <td>{app.namespace}</td>
                            <td>{app.deployed_at}</td>
                            <td>{app.status}</td>
                            <td>
                                <button onClick={() => handleDelete(app.id)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Applications;
