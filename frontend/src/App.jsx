import { BrowserRouter, Route, Routes, useParams } from 'react-router-dom'
import { JobProvider } from './store/useJob'
import Upload from './pages/Upload'
import Prepare from './pages/Prepare'
import Transcript from './pages/Transcript'
import Translate from './pages/Translate'
import Render from './pages/Render'

function JobRoute({ children }) {
  const { jobId } = useParams()
  return <JobProvider jobId={jobId}>{children}</JobProvider>
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-neutral-950 text-neutral-100">
        <Routes>
          <Route path="/" element={<Upload />} />
          <Route
            path="/jobs/:jobId/prepare"
            element={
              <JobRoute>
                <Prepare />
              </JobRoute>
            }
          />
          <Route
            path="/jobs/:jobId/transcript"
            element={
              <JobRoute>
                <Transcript />
              </JobRoute>
            }
          />
          <Route
            path="/jobs/:jobId/translate"
            element={
              <JobRoute>
                <Translate />
              </JobRoute>
            }
          />
          <Route
            path="/jobs/:jobId/render"
            element={
              <JobRoute>
                <Render />
              </JobRoute>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
