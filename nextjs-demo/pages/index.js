export default function Home() {
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
        Next.js Demo Application
      </h2>
      <div style={{
        background: '#f8f9fa',
        padding: '2rem',
        borderRadius: '10px',
        textAlign: 'center',
        maxWidth: '600px'
      }}>
        <p style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
          Welcome to your automatically deployed Next.js application!
        </p>
        <p style={{ color: '#6c757d' }}>
          This demo shows how AutoDeploy AI can detect and deploy Next.js projects to Vercel.
        </p>
        <div style={{ marginTop: '2rem', padding: '1rem', background: 'white', borderRadius: '6px' }}>
          <strong>Framework:</strong> Next.js<br/>
          <strong>Deployed to:</strong> Vercel<br/>
          <strong>Status:</strong> ✅ Live
        </div>
      </div>
    </div>
  )
}