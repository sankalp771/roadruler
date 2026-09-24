import { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import L from 'leaflet';
import 'leaflet.heat';
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet';
import { AlertTriangle, Layers, Map, RefreshCw, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import ComplaintActionModal from '../components/ComplaintActionModal';

const DEFAULT_CENTER = [19.076, 72.8777];

const ADMIN_DEMO_QUEUE = [
  { id: 'DEMO-1042', category: 'POTHOLE', ai_category: 'POTHOLE', description: 'Large pothole near the east bus stop', ward_id: 'Ward 12', status: 'RECEIVED', severity_level: 'CRITICAL', severity_score: 91, created_at: '2026-09-23T08:30:00Z' },
  { id: 'DEMO-1038', category: 'WATERLOGGING', ai_category: 'WATERLOGGING', description: 'Water collecting at the market crossing', ward_id: 'Ward 8', status: 'ASSIGNED', severity_level: 'CRITICAL', severity_score: 84, created_at: '2026-09-22T14:10:00Z' },
  { id: 'DEMO-1031', category: 'CRACK', ai_category: 'CRACK', description: 'Road surface crack spreading across lane', ward_id: 'Ward 4', status: 'IN_REPAIR', severity_level: 'MODERATE', severity_score: 63, created_at: '2026-09-21T10:00:00Z' },
  { id: 'DEMO-1024', category: 'POTHOLE', ai_category: 'POTHOLE', description: 'Pothole beside the community clinic', ward_id: 'Ward 12', status: 'PROCESSING', severity_level: 'MODERATE', severity_score: 58, created_at: '2026-09-20T09:20:00Z' },
  { id: 'DEMO-1019', category: 'CRACK', ai_category: 'CRACK', description: 'Small surface crack on service road', ward_id: 'Ward 2', status: 'RECEIVED', severity_level: 'MINOR', severity_score: 28, created_at: '2026-09-19T16:45:00Z' },
];

const ADMIN_DEMO_HOTSPOTS = {
  type: 'FeatureCollection',
  features: [
    { type: 'Feature', geometry: { type: 'Point', coordinates: [72.8777, 19.076] }, properties: { cluster_id: 'demo-1', complaint_count: 8, avg_severity: 72, dominant_category: 'POTHOLE', risk_level: 'HIGH_RISK_ZONE' } },
    { type: 'Feature', geometry: { type: 'Point', coordinates: [72.865, 19.083] }, properties: { cluster_id: 'demo-2', complaint_count: 4, avg_severity: 49, dominant_category: 'WATERLOGGING', risk_level: 'STANDARD_RISK_ZONE' } },
  ],
};

function formatDate(value) {
  if (!value) return 'Date unavailable';
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
}

function severityColor(level) {
  if (level === 'CRITICAL') return '#ef4444';
  if (level === 'MODERATE') return '#f59e0b';
  return '#eab308';
}

function HotspotHeatLayer({ features }) {
  const map = useMap();
  useEffect(() => {
    const points = features.map((feature) => {
      const [longitude, latitude] = feature.geometry.coordinates;
      const intensity = Math.min(1, feature.properties.complaint_count / 10);
      return [latitude, longitude, intensity];
    });
    const layer = L.heatLayer(points, {
      radius: 34,
      blur: 26,
      maxZoom: 17,
      gradient: { 0.2: '#facc15', 0.55: '#fb923c', 0.8: '#ef4444', 1: '#b91c1c' },
    });
    layer.addTo(map);
    return () => { map.removeLayer(layer); };
  }, [features, map]);
  return null;
}

export default function AuthorityDashboard({ demoPreview = false }) {
  const { getToken, isSignedIn, openSignInModal } = useAuth();
  const [queue, setQueue] = useState({ items: [], total: 0, page: 1, limit: 20, pages: 0 });
  const [hotspots, setHotspots] = useState({ type: 'FeatureCollection', features: [] });
  const [severity, setSeverity] = useState('');
  const [status, setStatus] = useState('');
  const [category, setCategory] = useState('');
  const [wardId, setWardId] = useState('');
  const [slaState, setSlaState] = useState('');
  const [searchText, setSearchText] = useState('');
  const [search, setSearch] = useState('');
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [page, setPage] = useState(1);
  const [heatmapEnabled, setHeatmapEnabled] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [requiresClerkAuth, setRequiresClerkAuth] = useState(false);
  const [previewActive, setPreviewActive] = useState(false);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const token = await getToken();
      if (!token) {
        if (demoPreview) {
          setPreviewActive(true);
          setQueue({ items: ADMIN_DEMO_QUEUE, total: ADMIN_DEMO_QUEUE.length, page: 1, limit: 20, pages: 1 });
          setHotspots(ADMIN_DEMO_HOTSPOTS);
          setRequiresClerkAuth(false);
          setError('Demo preview data only. Sign in with a verified Clerk Admin account to view live complaints and manage reports.');
          return;
        }
        setRequiresClerkAuth(true);
        setPreviewActive(false);
        setError('The local demo role cannot access protected authority data. Use Clerk with a Ward Officer or Admin role to continue.');
        return;
      }
      setRequiresClerkAuth(false);
      setPreviewActive(false);
      const headers = { Authorization: `Bearer ${token}` };
      const params = { page, limit: 20 };
      if (severity) params.severity = severity;
      if (status) params.status = status;
      if (category) params.category = category;
      if (wardId) params.ward_id = wardId;
      if (search) params.search = search;
      if (slaState) params.sla_state = slaState;
      const [queueResponse, hotspotsResponse] = await Promise.all([
        axios.get('/api/v1/authority/complaints', { headers, params }),
        axios.get('/api/v1/analytics/hotspots', { headers }),
      ]);
      setQueue(queueResponse.data);
      setHotspots(hotspotsResponse.data);
    } catch (requestError) {
      if (requestError.response?.status === 403) setError('Your verified account does not have Ward Officer or Admin access.');
      else if (requestError.response?.status === 401) { setRequiresClerkAuth(true); setError('Your Clerk session has expired. Sign in again to continue.'); }
      else setError('Could not load authority data. Check the API connection and try again.');
    } finally {
      setLoading(false);
    }
  }, [category, demoPreview, getToken, page, search, severity, slaState, status, wardId]);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);
  useEffect(() => {
    const timer = setTimeout(() => { setPage(1); setSearch(searchText.trim()); }, 300);
    return () => clearTimeout(timer);
  }, [searchText]);
  const criticalCount = useMemo(() => queue.items.filter((item) => item.severity_level === 'CRITICAL').length, [queue.items]);

  return (
    <div className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
      <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-300"><Shield className="h-3.5 w-3.5" /> Municipal Authority Console</div>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-white">Ward Officer Work Queue</h1>
          <p className="mt-1 text-sm text-gray-400">Live complaints ranked by severity, with DBSCAN hotspot zones.</p>
        </div>
        <button onClick={loadDashboard} disabled={loading} className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-700 bg-gray-800 px-4 py-2 text-sm font-medium text-gray-200 hover:bg-gray-700 disabled:opacity-50"><RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} /> Refresh</button>
      </header>

      {error && <div role="status" className="flex flex-col gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100 sm:flex-row sm:items-center sm:justify-between"><span>{error}</span>{(!isSignedIn || requiresClerkAuth) && <button onClick={openSignInModal} className="self-start rounded-lg bg-amber-400 px-3 py-2 font-semibold text-gray-950 sm:self-auto">Open sign in</button>}</div>}

      <section aria-label="Queue metrics" className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="glass-card rounded-2xl p-5"><div className="flex items-center justify-between text-xs font-semibold uppercase text-gray-400">Active complaints <Layers className="h-4 w-4 text-blue-400" /></div><div className="mt-2 text-3xl font-black text-white">{queue.total}</div><p className="mt-1 text-xs text-gray-500">Matching current filters</p></div>
        <div className="glass-card rounded-2xl p-5"><div className="flex items-center justify-between text-xs font-semibold uppercase text-gray-400">Critical on this page <AlertTriangle className="h-4 w-4 text-red-400" /></div><div className="mt-2 text-3xl font-black text-red-400">{criticalCount}</div><p className="mt-1 text-xs text-gray-500">Of {queue.items.length} displayed reports</p></div>
      </section>

      <section className="overflow-hidden rounded-2xl border border-gray-800 bg-gray-900/50">
        <div className="flex flex-col justify-between gap-3 border-b border-gray-800 p-4 sm:flex-row sm:items-center"><div><h2 className="text-sm font-bold uppercase tracking-wider text-white">Priority Queue</h2><p className="mt-1 text-xs text-gray-400">Showing {queue.items.length} of {queue.total} active complaints</p></div>
          <div className="flex flex-wrap gap-2"><label className="sr-only" htmlFor="authority-search">Search complaint ID or details</label><input id="authority-search" type="search" maxLength={100} value={searchText} onChange={(event) => setSearchText(event.target.value)} placeholder="Search ID or details" className="min-w-40 rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-xs text-white" />
            <label className="sr-only" htmlFor="authority-ward">Filter ward</label><input id="authority-ward" maxLength={64} value={wardId} onChange={(event) => { setPage(1); setWardId(event.target.value); }} placeholder="Ward ID" className="w-28 rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-xs text-white" />
            <label className="sr-only" htmlFor="authority-category">Filter hazard category</label><select id="authority-category" value={category} onChange={(event) => { setPage(1); setCategory(event.target.value); }} className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-xs text-white"><option value="">All categories</option><option value="POTHOLE">Pothole</option><option value="CRACK">Crack</option><option value="WATERLOGGING">Waterlogging</option></select>
            <label className="sr-only" htmlFor="authority-severity">Filter severity</label><select id="authority-severity" value={severity} onChange={(event) => { setPage(1); setSeverity(event.target.value); }} className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-xs text-white"><option value="">All severities</option><option>CRITICAL</option><option>MODERATE</option><option>MINOR</option></select>
            <label className="sr-only" htmlFor="authority-sla">Filter SLA state</label><select id="authority-sla" value={slaState} onChange={(event) => { setPage(1); setSlaState(event.target.value); }} className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-xs text-white"><option value="">All SLA states</option><option value="WITHIN_SLA">Within SLA</option><option value="OVERDUE">Overdue</option></select>
            <label className="sr-only" htmlFor="authority-status">Filter status</label><select id="authority-status" value={status} onChange={(event) => { setPage(1); setStatus(event.target.value); }} className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-xs text-white"><option value="">All active statuses</option><option>RECEIVED</option><option>PROCESSING</option><option>ASSIGNED</option><option>IN_REPAIR</option></select></div>
        </div>
        <div className="overflow-x-auto"><table className="w-full min-w-[850px] text-left text-sm"><thead className="bg-gray-950/70 text-xs uppercase text-gray-400"><tr><th className="px-4 py-3">Severity</th><th className="px-4 py-3">Complaint</th><th className="px-4 py-3">Ward</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Score</th><th className="px-4 py-3">Submitted</th><th className="px-4 py-3">Action</th></tr></thead>
          <tbody className="divide-y divide-gray-800">{queue.items.map((item) => <tr key={item.id} className="hover:bg-gray-800/40"><td className="px-4 py-4"><span className="rounded-md border px-2 py-1 text-[10px] font-bold" style={{ color: severityColor(item.severity_level), borderColor: `${severityColor(item.severity_level)}55`, backgroundColor: `${severityColor(item.severity_level)}12` }}>{item.severity_level}</span></td><td className="px-4 py-4"><div className="font-semibold text-white">{item.ai_category || item.category}</div><div className="mt-1 max-w-xs truncate text-xs text-gray-500">{item.description || item.id}</div></td><td className="px-4 py-4 text-gray-300">{item.ward_id || 'Unassigned'}</td><td className="px-4 py-4 text-gray-300">{item.status}</td><td className="px-4 py-4 font-mono text-gray-200">{Number(item.severity_score).toFixed(1)}</td><td className="px-4 py-4 text-xs text-gray-400">{formatDate(item.created_at)}</td><td className="px-4 py-4">{previewActive ? <span className="text-xs text-gray-500">Preview only</span> : <button onClick={() => setSelectedComplaint(item)} className="rounded-lg border border-blue-500/30 px-3 py-1.5 text-xs font-semibold text-blue-300 hover:bg-blue-500/10">Manage</button>}</td></tr>)}
            {!loading && queue.items.length === 0 && <tr><td colSpan="7" className="px-4 py-10 text-center text-sm text-gray-500">No complaints match these filters.</td></tr>}</tbody></table></div>
        <div className="flex items-center justify-between border-t border-gray-800 px-4 py-3 text-xs text-gray-400"><span>Page {queue.page} of {Math.max(queue.pages, 1)}</span><div className="flex gap-2"><button disabled={page <= 1 || loading} onClick={() => setPage((current) => current - 1)} className="rounded-lg border border-gray-700 px-3 py-1.5 disabled:opacity-40">Previous</button><button disabled={page >= queue.pages || loading} onClick={() => setPage((current) => current + 1)} className="rounded-lg border border-gray-700 px-3 py-1.5 disabled:opacity-40">Next</button></div></div>
      </section>

      <section className="overflow-hidden rounded-2xl border border-gray-800 bg-gray-900/50"><div className="flex items-center justify-between border-b border-gray-800 p-4"><div><h2 className="text-sm font-bold uppercase tracking-wider text-white">Spatial Hotspots</h2><p className="mt-1 text-xs text-gray-400">Clusters contain at least three active complaints within 50 metres.</p></div><button aria-pressed={heatmapEnabled} onClick={() => setHeatmapEnabled((enabled) => !enabled)} className="inline-flex items-center gap-2 rounded-lg border border-gray-700 px-3 py-2 text-xs text-gray-200"><Map className="h-4 w-4" />{heatmapEnabled ? 'Hide overlay' : 'Show overlay'}</button></div>
        <div className="h-[380px]"><MapContainer center={DEFAULT_CENTER} zoom={12} scrollWheelZoom className="h-full w-full"><TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {heatmapEnabled && <HotspotHeatLayer features={hotspots.features} />}
          {heatmapEnabled && hotspots.features.map((feature) => { const [longitude, latitude] = feature.geometry.coordinates; const properties = feature.properties; const color = properties.risk_level === 'HIGH_RISK_ZONE' ? '#ef4444' : '#eab308'; return <CircleMarker key={properties.cluster_id} center={[latitude, longitude]} radius={6} pathOptions={{ color: '#fff', fillColor: color, fillOpacity: 1, weight: 1 }}><Popup><strong>{properties.risk_level}</strong><br />{properties.complaint_count} complaints · Avg severity {properties.avg_severity}<br />Main category: {properties.dominant_category}</Popup></CircleMarker>; })}
        </MapContainer></div><p className="px-4 py-3 text-xs text-gray-500">{hotspots.features.length} clusters · red indicates average severity above 60; yellow indicates standard risk.</p>
      </section>
      {selectedComplaint && <ComplaintActionModal complaint={selectedComplaint} getToken={getToken} onClose={() => setSelectedComplaint(null)} onUpdated={loadDashboard} />}
    </div>
  );
}
