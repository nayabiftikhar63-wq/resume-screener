import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../api.js';
import { useToast } from '../components/ToastProvider.jsx';
import Modal from '../components/Modal.jsx';
import Loading from '../components/Loading.jsx';
import { getScoreClass, getRecClass } from '../utils/screening.js';

const EMPTY_STATS = {
  total_jobs: 0,
  total_applications: 0,
  screened_applications: 0,
  average_score: 0,
};

const EMPTY_JOB_FORM = {
  title: '',
  company: '',
  location: '',
  job_type: 'Full-time',
  salary_range: '',
  description: '',
  requirements: '',
};

export default function Admin() {
  const showToast = useToast();

  const [stats, setStats] = useState(EMPTY_STATS);
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [applications, setApplications] = useState([]);

  const [loading, setLoading] = useState({ active: false, message: '' });

  const [addJobOpen, setAddJobOpen] = useState(false);
  const [jobForm, setJobForm] = useState(EMPTY_JOB_FORM);

  const [detailApp, setDetailApp] = useState(null);

  // Candidate email drafting (scoped to the currently-open detail modal).
  const [emailDraft, setEmailDraft] = useState(null); // { subject, body, kind }
  const [emailLoading, setEmailLoading] = useState(false);

  const refreshStats = useCallback(async () => {
    try {
      setStats(await api.getStats());
    } catch {
      // non-fatal
    }
  }, []);

  const refreshJobs = useCallback(async () => {
    try {
      setJobs(await api.listJobs());
    } catch {
      showToast('Failed to load jobs', 'error');
    }
  }, [showToast]);

  const refreshSelected = useCallback(
    async (jobId) => {
      if (!jobId) {
        setSelectedJob(null);
        setApplications([]);
        return;
      }
      try {
        const [job, apps] = await Promise.all([
          api.getJob(jobId),
          api.listApplications(jobId),
        ]);
        setSelectedJob(job);
        setApplications(apps);
      } catch {
        showToast('Failed to load applications', 'error');
      }
    },
    [showToast]
  );

  useEffect(() => {
    refreshJobs();
    refreshStats();
  }, [refreshJobs, refreshStats]);

  useEffect(() => {
    refreshSelected(selectedJobId);
  }, [selectedJobId, refreshSelected]);

  const sortedApps = useMemo(() => {
    return [...applications].sort((a, b) => {
      if (a.screened && !b.screened) return -1;
      if (!a.screened && b.screened) return 1;
      return (b.ai_score || 0) - (a.ai_score || 0);
    });
  }, [applications]);

  const unscreenedCount = useMemo(
    () => applications.filter((a) => !a.screened).length,
    [applications]
  );
  const screenedCount = applications.length - unscreenedCount;

  async function onCreateJob(e) {
    e.preventDefault();
    try {
      await api.createJob({
        ...jobForm,
        salary_range: jobForm.salary_range || null,
      });
      setAddJobOpen(false);
      setJobForm(EMPTY_JOB_FORM);
      await Promise.all([refreshJobs(), refreshStats()]);
      showToast('Job created!');
    } catch {
      showToast('Failed to create job', 'error');
    }
  }

  async function onDeleteJob(jobId) {
    if (!window.confirm('Delete this job and all its applications?')) return;
    try {
      await api.deleteJob(jobId);
      setSelectedJobId(null);
      await Promise.all([refreshJobs(), refreshStats()]);
      showToast('Job deleted');
    } catch {
      showToast('Delete failed', 'error');
    }
  }

  async function onScreenAll(jobId, { force = false } = {}) {
    if (force) {
      const ok = window.confirm(
        `Re-screen all ${applications.length} resume${applications.length === 1 ? '' : 's'} for this job? ` +
          'This will overwrite the existing AI scores and call Gemini again for each candidate.'
      );
      if (!ok) return;
    }
    setLoading({
      active: true,
      message: force
        ? 'Re-screening all resumes with Gemini AI…'
        : 'Screening resumes with Gemini AI…',
    });
    try {
      await api.screenAll(jobId, { force });
      showToast(
        force ? 'All resumes re-screened!' : 'All resumes screened successfully!'
      );
      await Promise.all([refreshSelected(jobId), refreshStats()]);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading({ active: false, message: '' });
    }
  }

  async function onScreenOne(appId, { rescreen = false } = {}) {
    if (rescreen) {
      const ok = window.confirm(
        'Re-screen this resume? The existing AI score and analysis will be overwritten.'
      );
      if (!ok) return;
    }
    closeDetailModal();
    setLoading({
      active: true,
      message: rescreen
        ? 'Re-screening resume with Gemini AI…'
        : 'Screening resume with Gemini AI…',
    });
    try {
      await api.screenOne(appId);
      showToast(rescreen ? 'Resume re-screened!' : 'Resume screened!');
      await Promise.all([refreshSelected(selectedJobId), refreshStats()]);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading({ active: false, message: '' });
    }
  }

  const setJobFormField = (key) => (e) =>
    setJobForm((f) => ({ ...f, [key]: e.target.value }));

  // ── Email drafting ───────────────────────────────────────────
  function defaultEmailKind(application) {
    const rec = (application?.ai_recommendation || '').toLowerCase();
    if (rec.includes('no hire')) return 'decline';
    return 'interview';
  }

  function closeDetailModal() {
    setDetailApp(null);
    setEmailDraft(null);
    setEmailLoading(false);
  }

  async function onDraftEmail(kind) {
    if (!detailApp) return;
    setEmailLoading(true);
    try {
      const draft = await api.draftEmail(detailApp.id, kind);
      setEmailDraft({ ...draft, kind });
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setEmailLoading(false);
    }
  }

  async function copyToClipboard(text, label) {
    try {
      await navigator.clipboard.writeText(text);
      showToast(`${label} copied to clipboard`);
    } catch {
      showToast('Copy failed — please select and copy manually', 'error');
    }
  }

  return (
    <div className="container">
      <div style={{ paddingTop: 32 }}>
        <div className="stats-grid">
          <StatCard
            icon="📋"
            iconStyle={{ background: 'var(--info-bg)', color: 'var(--info)' }}
            label="Total Jobs"
            value={stats.total_jobs}
          />
          <StatCard
            icon="📨"
            iconStyle={{ background: 'rgba(13,148,136,0.08)', color: 'var(--accent)' }}
            label="Applications"
            value={stats.total_applications}
          />
          <StatCard
            icon="🤖"
            iconStyle={{ background: 'var(--success-bg)', color: 'var(--success)' }}
            label="Screened"
            value={stats.screened_applications}
          />
          <StatCard
            icon="⭐"
            iconStyle={{ background: 'var(--warning-bg)', color: 'var(--warning)' }}
            label="Avg Score"
            value={stats.average_score}
          />
        </div>
      </div>

      <div className="admin-grid">
        <div className="admin-sidebar">
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 16,
            }}
          >
            <h3 style={{ margin: 0 }}>Jobs</h3>
            <button
              className="btn btn-primary btn-sm"
              onClick={() => setAddJobOpen(true)}
            >
              + Add Job
            </button>
          </div>
          <div>
            {jobs.length === 0 ? (
              <p
                style={{
                  color: 'var(--text-muted)',
                  fontSize: '0.85rem',
                  textAlign: 'center',
                  padding: 20,
                }}
              >
                No jobs yet. Click "+ Add Job" to create one.
              </p>
            ) : (
              jobs.map((j) => (
                <div
                  key={j.id}
                  className={`admin-job-item${selectedJobId === j.id ? ' active' : ''}`}
                  onClick={() => setSelectedJobId(j.id)}
                >
                  <h4>{j.title}</h4>
                  <p>
                    {j.company} · {j.applications_count} app
                    {j.applications_count !== 1 ? 's' : ''}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="admin-main">
          {!selectedJob ? (
            <div className="empty-state">
              <div className="empty-icon">👈</div>
              <h3>Select a job from the sidebar</h3>
              <p>View applications and run AI screening.</p>
            </div>
          ) : (
            <>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: 24,
                  flexWrap: 'wrap',
                  gap: 12,
                }}
              >
                <div>
                  <h2>{selectedJob.title}</h2>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    {selectedJob.company} · {selectedJob.location}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {unscreenedCount > 0 && (
                    <button
                      className="btn btn-success"
                      onClick={() => onScreenAll(selectedJob.id)}
                    >
                      🤖 Screen {unscreenedCount} Resume
                      {unscreenedCount > 1 ? 's' : ''}
                    </button>
                  )}
                  {screenedCount > 0 && (
                    <button
                      className="btn btn-secondary"
                      onClick={() => onScreenAll(selectedJob.id, { force: true })}
                      title="Re-run Gemini screening on every application (overwrites current scores)"
                    >
                      🔄 Re-screen all
                    </button>
                  )}
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => onDeleteJob(selectedJob.id)}
                  >
                    Delete Job
                  </button>
                </div>
              </div>

              {applications.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">📭</div>
                  <h3>No applications yet</h3>
                  <p>Share the job link so candidates can apply.</p>
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table className="app-table">
                    <thead>
                      <tr>
                        <th>Candidate</th>
                        <th>Resume</th>
                        <th>Score</th>
                        <th>Recommendation</th>
                        <th>Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sortedApps.map((a) => (
                        <tr
                          key={a.id}
                          onClick={() => setDetailApp(a)}
                          style={{ cursor: 'pointer' }}
                        >
                          <td>
                            <strong style={{ color: 'var(--text-primary)' }}>{a.name}</strong>
                            <br />
                            <span style={{ fontSize: '0.75rem' }}>{a.email}</span>
                          </td>
                          <td>{a.resume_filename}</td>
                          <td>
                            {a.screened ? (
                              <span className={`score-badge ${getScoreClass(a.ai_score)}`}>
                                {a.ai_score}
                              </span>
                            ) : (
                              <span style={{ color: 'var(--text-muted)' }}>—</span>
                            )}
                          </td>
                          <td>
                            {a.screened ? (
                              <span className={`rec-badge ${getRecClass(a.ai_recommendation)}`}>
                                {a.ai_recommendation}
                              </span>
                            ) : (
                              <span style={{ color: 'var(--text-muted)' }}>Pending</span>
                            )}
                          </td>
                          <td>
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                              {new Date(a.applied_at).toLocaleDateString()}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Add Job Modal */}
      <Modal open={addJobOpen} onClose={() => setAddJobOpen(false)}>
        <div className="modal-header">
          <h3>Add New Job</h3>
          <button className="modal-close" onClick={() => setAddJobOpen(false)}>
            ✕
          </button>
        </div>
        <form onSubmit={onCreateJob}>
          <div className="form-group">
            <label>Job Title *</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. Software Engineer"
              value={jobForm.title}
              onChange={setJobFormField('title')}
              required
            />
          </div>
          <div className="form-group">
            <label>Company *</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. Acme Corp"
              value={jobForm.company}
              onChange={setJobFormField('company')}
              required
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label>Location *</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g. Remote"
                value={jobForm.location}
                onChange={setJobFormField('location')}
                required
              />
            </div>
            <div className="form-group">
              <label>Job Type *</label>
              <select
                className="form-control"
                value={jobForm.job_type}
                onChange={setJobFormField('job_type')}
                required
              >
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
                <option value="Remote">Remote</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Salary Range</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. $80,000 - $120,000"
              value={jobForm.salary_range}
              onChange={setJobFormField('salary_range')}
            />
          </div>
          <div className="form-group">
            <label>Job Description *</label>
            <textarea
              className="form-control"
              placeholder="Describe the role, responsibilities…"
              value={jobForm.description}
              onChange={setJobFormField('description')}
              required
            />
          </div>
          <div className="form-group">
            <label>Requirements *</label>
            <textarea
              className="form-control"
              placeholder="List skills, experience needed…"
              value={jobForm.requirements}
              onChange={setJobFormField('requirements')}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%' }}>
            Create Job Posting
          </button>
        </form>
      </Modal>

      {/* Application Detail Modal */}
      <Modal open={!!detailApp} onClose={closeDetailModal}>
        {detailApp && (
          <>
            <div className="modal-header">
              <h3>{detailApp.name}</h3>
              <button className="modal-close" onClick={closeDetailModal}>
                ✕
              </button>
            </div>
            <div
              style={{
                display: 'flex',
                gap: 12,
                flexWrap: 'wrap',
                marginBottom: 20,
              }}
            >
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                📧 {detailApp.email}
              </span>
              {detailApp.phone && (
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  📱 {detailApp.phone}
                </span>
              )}
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                📄 {detailApp.resume_filename}
              </span>
            </div>

            {detailApp.screened ? (
              <>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 16,
                    marginBottom: 20,
                  }}
                >
                  <span
                    className={`score-badge ${getScoreClass(detailApp.ai_score)}`}
                    style={{ width: 64, height: 64, fontSize: '1.3rem' }}
                  >
                    {detailApp.ai_score}
                  </span>
                  <div>
                    <span
                      className={`rec-badge ${getRecClass(detailApp.ai_recommendation)}`}
                      style={{
                        fontSize: '0.85rem',
                        marginBottom: 8,
                        display: 'inline-block',
                      }}
                    >
                      {detailApp.ai_recommendation}
                    </span>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                      {detailApp.ai_summary}
                    </p>
                  </div>
                </div>
                <div className="detail-panel">
                  <h4>✅ Strengths</h4>
                  <ul>
                    {(detailApp.ai_strengths || []).map((s, i) => (
                      <li key={i} className="strength-item">
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="detail-panel">
                  <h4>⚠️ Weaknesses</h4>
                  <ul>
                    {(detailApp.ai_weaknesses || []).map((w, i) => (
                      <li key={i} className="weakness-item">
                        {w}
                      </li>
                    ))}
                  </ul>
                </div>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'flex-end',
                    gap: 8,
                    marginTop: 8,
                    flexWrap: 'wrap',
                  }}
                >
                  {!emailDraft && !emailLoading && (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => onDraftEmail(defaultEmailKind(detailApp))}
                      title="Use Gemini to draft a candidate-facing email"
                    >
                      📧 Draft email
                    </button>
                  )}
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() =>
                      onScreenOne(detailApp.id, { rescreen: true })
                    }
                    title="Re-run Gemini screening for this candidate"
                  >
                    🔄 Re-screen this resume
                  </button>
                </div>

                {(emailLoading || emailDraft) && (
                  <div className="detail-panel" style={{ marginTop: 16 }}>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        gap: 8,
                        marginBottom: 12,
                        flexWrap: 'wrap',
                      }}
                    >
                      <h4 style={{ margin: 0 }}>📧 Draft email to {detailApp.name}</h4>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {[
                          { id: 'interview', label: 'Next step' },
                          { id: 'offer', label: 'Offer' },
                          { id: 'decline', label: 'Decline' },
                        ].map((tone) => {
                          const active = emailDraft?.kind === tone.id;
                          return (
                            <button
                              key={tone.id}
                              type="button"
                              className={`btn btn-sm ${active ? 'btn-primary' : 'btn-secondary'}`}
                              disabled={emailLoading}
                              onClick={() => onDraftEmail(tone.id)}
                            >
                              {tone.label}
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {emailLoading ? (
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 10,
                          color: 'var(--text-muted)',
                          fontSize: '0.875rem',
                          padding: '12px 0',
                        }}
                      >
                        <div className="spinner" /> Drafting email with Gemini…
                      </div>
                    ) : (
                      <>
                        <div className="form-group" style={{ marginBottom: 12 }}>
                          <label>Subject</label>
                          <input
                            type="text"
                            className="form-control"
                            value={emailDraft.subject}
                            onChange={(e) =>
                              setEmailDraft({ ...emailDraft, subject: e.target.value })
                            }
                          />
                        </div>
                        <div className="form-group" style={{ marginBottom: 12 }}>
                          <label>Body</label>
                          <textarea
                            className="form-control"
                            style={{ minHeight: 220, fontFamily: 'inherit', whiteSpace: 'pre-wrap' }}
                            value={emailDraft.body}
                            onChange={(e) =>
                              setEmailDraft({ ...emailDraft, body: e.target.value })
                            }
                          />
                        </div>
                        <div
                          style={{
                            display: 'flex',
                            gap: 8,
                            justifyContent: 'flex-end',
                            flexWrap: 'wrap',
                          }}
                        >
                          <button
                            type="button"
                            className="btn btn-secondary btn-sm"
                            onClick={() => setEmailDraft(null)}
                          >
                            ✕ Close
                          </button>
                          <button
                            type="button"
                            className="btn btn-secondary btn-sm"
                            onClick={() => onDraftEmail(emailDraft.kind)}
                          >
                            🔄 Regenerate
                          </button>
                          <button
                            type="button"
                            className="btn btn-secondary btn-sm"
                            onClick={() =>
                              copyToClipboard(emailDraft.subject, 'Subject')
                            }
                          >
                            📋 Copy subject
                          </button>
                          <button
                            type="button"
                            className="btn btn-primary btn-sm"
                            onClick={() =>
                              copyToClipboard(emailDraft.body, 'Email body')
                            }
                          >
                            📋 Copy body
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="empty-state" style={{ padding: 30 }}>
                <p>This resume hasn't been screened yet.</p>
                <button
                  className="btn btn-primary"
                  style={{ marginTop: 12 }}
                  onClick={() => onScreenOne(detailApp.id)}
                >
                  🤖 Screen Now
                </button>
              </div>
            )}
          </>
        )}
      </Modal>

      <Loading active={loading.active} message={loading.message} />
    </div>
  );
}

function StatCard({ icon, iconStyle, label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-icon" style={iconStyle}>
        {icon}
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
