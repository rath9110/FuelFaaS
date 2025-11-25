import Link from 'next/link';

export default function Home() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, var(--primary-600) 0%, var(--secondary-600) 100%)',
      padding: 'var(--spacing-xl)'
    }}>
      <div style={{
        maxWidth: '600px',
        textAlign: 'center',
        color: 'white'
      }}>
        <h1 style={{
          fontSize: '4rem',
          fontWeight: '800',
          marginBottom: 'var(--spacing-lg)',
          textShadow: '0 2px 10px rgba(0,0,0,0.2)'
        }}>
          ⛽ FuelGuard AI
        </h1>
        <p style={{
          fontSize: '1.5rem',
          marginBottom: 'var(--spacing-2xl)',
          opacity: 0.95
        }}>
          Advanced Fuel Fraud Detection for Construction & Transport
        </p>
        <p style={{
          fontSize: '1.125rem',
          marginBottom: 'var(--spacing-2xl)',
          opacity: 0.9,
          lineHeight: '1.6'
        }}>
          Real-time anomaly detection using AI-powered rules to identify suspicious fuel transactions,
          saving companies money and providing evidence for HR, finance, and legal teams.
        </p>
        <Link
          href="/dashboard"
          className="btn"
          style={{
            background: 'white',
            color: 'var(--primary-600)',
            fontSize: '1.125rem',
            padding: 'var(--spacing-md) var(--spacing-2xl)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            fontWeight: '600'
          }}
        >
          Go to Dashboard →
        </Link>
      </div>
    </div>
  );
}
