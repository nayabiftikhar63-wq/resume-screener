import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api.js';
import { useToast } from '../components/ToastProvider.jsx';
import Modal from '../components/Modal.jsx';
import Loading from '../components/Loading.jsx';

export default function Apply() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const showToast = useToast();

  const [job, setJob] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState(null);
  const [form, setForm] = useState({ name: '', email: '', phone: '' });
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!jobId) {
      navigate('/');
      return;
    }
    api
      .getJob(jobId)
      .then(setJob)
      .catch(() => navigate('/'));
  }, [jobId, navigate]);

  const onField = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const onPickFile = (e) => {
    const f = e.target.files?.[0];
    if (f) setFile(f);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) setFile(f);
  };

  async function onSubmit(e) {
    e.preventDefault();
    if (!file) {
      showToast('Please upload your resume PDF', 'error');
      return;
    }
    setSubmitting(true);
    try {
      const fd = new FormData();
      fd.append('name', form.name);
      fd.append('email', form.email);
      fd.append('phone', form.phone || '');
      fd.append('resume', file);
      await api.applyToJob(jobId, fd);
      setSuccess(true);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="container">
      <div className="apply-layout">
        <div className="job-details card">
          {!job ? (
            <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
              Loading job details…
            </div>
          ) : (
            <>
              <span
                className="job-type-badge"
                style={{ marginBottom: 16, display: 'inline-block' }}
              >
                {job.job_type}
              </span>
              <h2>{job.title}</h2>
              <div className="job-meta" style={{ margin: '12px 0 24px' }}>
                <span>🏢 {job.company}</span>
                <span>📍 {job.location}</span>
                {job.salary_range && <span>💰 {job.salary_range}</span>}
              </div>
              <div className="section-block">
                <h4>Description</h4>
                <p>{job.description}</p>
              </div>
              <div className="section-block">
                <h4>Requirements</h4>
                <p>{job.requirements}</p>
              </div>
            </>
          )}
        </div>

        <div>
          <div className="card">
            <h3 style={{ marginBottom: 24 }}>Submit Your Application</h3>
            <form onSubmit={onSubmit}>
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input
                  id="name"
                  type="text"
                  className="form-control"
                  placeholder="John Doe"
                  value={form.name}
                  onChange={onField('name')}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email Address *</label>
                <input
                  id="email"
                  type="email"
                  className="form-control"
                  placeholder="john@example.com"
                  value={form.email}
                  onChange={onField('email')}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  id="phone"
                  type="tel"
                  className="form-control"
                  placeholder="+1 (555) 123-4567"
                  value={form.phone}
                  onChange={onField('phone')}
                />
              </div>
              <div className="form-group">
                <label>Resume (PDF) *</label>
                <div
                  className={`file-upload${dragOver ? ' dragover' : ''}`}
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragOver(true);
                  }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={onDrop}
                >
                  <div className="file-upload-icon">📄</div>
                  <p>
                    Drag &amp; drop your resume here or{' '}
                    <strong style={{ color: 'var(--accent)' }}>browse</strong>
                  </p>
                  {file && <p className="file-name">📎 {file.name}</p>}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf"
                    style={{ display: 'none' }}
                    onChange={onPickFile}
                  />
                </div>
              </div>
              <button
                type="submit"
                className="btn btn-primary btn-lg"
                style={{ width: '100%' }}
                disabled={submitting}
              >
                Submit Application
              </button>
            </form>
          </div>
        </div>
      </div>

      <Modal open={success} onClose={() => setSuccess(false)}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: 16 }}>🎉</div>
          <h2 style={{ marginBottom: 12 }}>Application Submitted!</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
            Your resume has been received and will be screened by our AI system. Good luck!
          </p>
          <Link to="/" className="btn btn-primary">
            Back to Jobs
          </Link>
        </div>
      </Modal>

      <Loading active={submitting} message="Submitting your application…" />
    </div>
  );
}
