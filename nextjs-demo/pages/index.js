import { useEffect, useState } from "react";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    async function checkBackend() {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
        const data = await res.json();
        if (data.status === "healthy") {
          setBackendStatus("✅ Connected to Backend");
        } else {
          setBackendStatus("⚠️ Backend Responded But Unhealthy");
        }
      } catch (err) {
        setBackendStatus("❌ Cannot Reach Backend");
      }
    }
    checkBackend();
  }, []);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '2rem',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1 style={{ fontSize: '3rem', color: '#667eea', marginBottom: '1rem' }}>
        🚀 AutoDeploy AI
      </h1>
      <h2 style={{ fontSize: '1.5rem', color: '#333', marginBottom: '2rem' }}>
        Next.js Demo Application (with Live Backend Test)
      </h2>

      <div style={{
        background: '#f8f9fa',
        padding: '2rem',
        borderRadius: '10px',
        textAlign: 'center',
        maxWidth: '600px'
      }}>
        <p style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
          Welcome to your deployed Next.js + Flask full-stack MVP!
        </p>

        <div style={{
          marginTop: '2rem',
          padding: '1rem',
          background: 'white',
          borderRadius: '6px'
        }}>
          <strong>Backend Status:</strong> {backendStatus}
        </div>
      </div>
    </div>
  );
}

