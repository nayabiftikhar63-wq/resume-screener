import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import JobsList from './pages/JobsList.jsx';
import Apply from './pages/Apply.jsx';
import Admin from './pages/Admin.jsx';

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<JobsList />} />
        <Route path="/apply/:jobId" element={<Apply />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="*" element={<JobsList />} />
      </Routes>
    </>
  );
}
