import React from 'react';

function SimpleTest() {
  return (
    <div style={{
      padding: '40px',
      background: '#1e1e2e',
      color: '#e4e4e7',
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{color: '#4285f4'}}>✅ React is Working!</h1>
      <p>If you see this, the frontend is loaded correctly.</p>
      <p>Backend API: <a href="http://localhost:5000" target="_blank" style={{color: '#4285f4'}}>http://localhost:5000</a></p>
      <p>Current time: {new Date().toLocaleTimeString()}</p>
    </div>
  );
}

export default SimpleTest;
