import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from '../components/ToastProvider.jsx';

export default function JobsList() {
  const [jobs, setJobs] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const showToast = useToast();

  useEffect(() => {
    api
      .listJobs()
      .then(setJobs)
      .catch(() => showToast('Failed to load jobs', 'error'))
      .finally(() => setLoaded(true));
  }, [showToast]);

  return (
    <>
      <section className="hero">
        <div className="container">
          <div className="hero-badge">
            <span className="pulse" /> AI-Powered Screening
          </div>
          <h1>Find Your Dream Job</h1>
          <p>
            Browse open positions and submit your resume. Our AI evaluates candidates fairly and
            instantly.
          </p>
        </div>
      </section>

      <section className="container">
        <div className="section-header">
          <h2>Open Positions</h2>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            {jobs.length > 0 && `${jobs.length} position${jobs.length > 1 ? 's' : ''}`}
          </span>
        </div>

        {loaded && jobs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No open positions right now</h3>
            <p>Check back soon or visit the admin portal to add jobs.</p>
          </div>
        ) : (
          <div className="jobs-grid">
            {jobs.map((job) => (
              <Link
                key={job.id}
                to={`/apply/${job.id}`}
                className="card job-card"
                style={{ color: 'inherit' }}
              >
                <div className="job-card-header">
                  <h3>{job.title}</h3>
                </div>
                <div className="job-meta" style={{ flexDirection: 'column', gap: 4 }}>
                  <span>🏢 {job.company}</span>
                  <span>📍 {job.location}</span>
                  <span className="job-type-badge" style={{ alignSelf: 'flex-start' }}>{job.job_type}</span>
                </div>
                <p className="job-description">{job.description}</p>
                <div className="job-card-apply">
                  {job.salary_range && (
                    <span className="salary">{job.salary_range}</span>
                  )}
                  <span className="btn btn-primary btn-sm" style={{ width: '100%' }}>Apply Now →</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
