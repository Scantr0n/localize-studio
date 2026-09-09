import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import { api } from '../utils/api'

const JobContext = createContext(null)

const POLLING_STATUSES = new Set(['preparing', 'transcribing', 'translating', 'rendering'])

export function JobProvider({ jobId, children }) {
  const [job, setJob] = useState(null)
  const intervalRef = useRef(null)

  const refresh = useCallback(async () => {
    if (!jobId) return
    const data = await api.getJob(jobId)
    setJob(data)
    return data
  }, [jobId])

  useEffect(() => {
    if (!jobId) return
    refresh()
  }, [jobId, refresh])

  useEffect(() => {
    if (!job) return
    const shouldPoll = POLLING_STATUSES.has(job.status)
    if (shouldPoll && !intervalRef.current) {
      intervalRef.current = setInterval(refresh, 1500)
    }
    if (!shouldPoll && intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [job, refresh])

  return <JobContext.Provider value={{ job, refresh }}>{children}</JobContext.Provider>
}

export function useJob() {
  const ctx = useContext(JobContext)
  if (!ctx) throw new Error('useJob must be used within JobProvider')
  return ctx
}
