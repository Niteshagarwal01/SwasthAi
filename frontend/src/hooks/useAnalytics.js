import { useEffect, useState, useCallback, useMemo } from 'react'
import { getAnalyticsSummary, getTopSymptoms, getRegional, getTimeline, getAlerts, getChannels } from '../services/api'

export function useAnalytics(autoRefreshMs = 30000) {
  const [summary, setSummary] = useState(null)
  const [symptoms, setSymptoms] = useState([])
  const [regional, setRegional] = useState([])
  const [timeline, setTimeline] = useState([])
  const [alerts, setAlerts] = useState([])
  const [channels, setChannels] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchAll = useCallback(async () => {
    try {
      const [s, sym, reg, tl, al, ch] = await Promise.all([
        getAnalyticsSummary(),
        getTopSymptoms(),
        getRegional(),
        getTimeline(),
        getAlerts(),
        getChannels(),
      ])
      setSummary(s); setSymptoms(sym); setRegional(reg)
      setTimeline(tl); setAlerts(al); setChannels(ch)
      setLastUpdated(new Date())
    } catch (e) {
      console.error('[Analytics] fetch error:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAll()
    if (autoRefreshMs > 0) {
      const interval = setInterval(fetchAll, autoRefreshMs)
      return () => clearInterval(interval)
    }
  }, [fetchAll, autoRefreshMs])

  return { summary, symptoms, regional, timeline, alerts, channels, loading, lastUpdated, refetch: fetchAll }
}

export function useCases(params = {}) {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const stableParams = useMemo(() => params, [JSON.stringify(params)])

  useEffect(() => {
    import('../services/api').then(({ getCases }) => {
      getCases(stableParams).then(data => { setCases(data); setLoading(false) }).catch(() => setLoading(false))
    })
  }, [stableParams])

  return { cases, loading }
}
