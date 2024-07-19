import React, { useState } from 'react';
import axios from 'axios';

const RegisterForm = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [registrationMessage, setRegistrationMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('full_name', fullName);
    formData.append('email', email);
    formData.append('password', password);
    formData.append('phone', phone);
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://127.0.0.1:8000/register/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setRegistrationMessage(response.data.message);
    } catch (error) {
      console.error(error);
      setRegistrationMessage('An error occurred during registration.');
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="fullName">Full Name:</label>
      <input
        type="text"
        id="fullName"
        name="fullName"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
        required
      />
      <label htmlFor="email">Email:</label>
      <input
        type="email"
        id="email"
        name="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <label htmlFor="password">Password:</label>
      <input
        type="password"
        id="password"
        name="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <label htmlFor="phone">Phone:</label>
      <input
        type="tel"
        id="phone"
        name="phone"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        required
      />
      <label htmlFor="profilePicture">Profile Picture:</label>
      <input
        type="file"
        id="profilePicture"
        name="file"
        onChange={handleFileChange}
      />
      <button type="submit">Register</button>
      {registrationMessage && <p>{registrationMessage}</p>}
    </form>
  );
};

export default RegisterForm;
