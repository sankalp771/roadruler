import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Search, MapPin, CheckCircle2, Clock, ShieldAlert, Cpu, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const STATUS_STEPS = [
  { value: 'PROCESSING', label: 'Report received', detail: 'AI analysis is queued.', icon: Cpu },
  { value: 'RECEIVED', label: 'Report analyzed', detail: 'The report is ready for municipal review.', icon: CheckCircle2 },
  { value: 'ASSIGNED', label: 'Assigned to an authority', detail: 'A municipal team has accepted the report.', icon: MapPin },
  { value: 'IN_REPAIR', label: 'Repair in progress', detail: 'The reported issue is being repaired.', icon: Clock },
  { value: 'RESOLVED', label: 'Resolved', detail: 'The repair has been marked complete.', icon: CheckCircle2 },
];

export default function TrackComplaint() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [complaintId, setComplaintId] = useState(searchParams.get('id') || '');
  const [lookupId, setLookupId] = useState(searchParams.get('id') || '');
  const [complaint, setComplaint] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { getToken } = useAuth();

  useEffect(() => {
    const idFromUrl = searchParams.get('id')?.trim() || '';
    setComplaintId(idFromUrl);
    setLookupId(idFromUrl);
  }, [searchParams]);

  useEffect(() => {
    if (!lookupId) {
      setComplaint(null);
      setError('');
      setIsLoading(false);
      return undefined;
    }

    let isCurrentRequest = true;
    let timeoutId;
    let hasLoadedComplaint = false;
    let shouldPollForAnalysis = false;

    const loadComplaint = async (showLoading = false) => {
      if (showLoading) setIsLoading(true);
      try {
        const token = await getToken();
        if (!token) {
          throw new Error('Sign in with your Clerk account to view your report.');
        }
        const response = await axios.get(`/api/v1/complaints/${encodeURIComponent(lookupId)}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!isCurrentRequest) return;
        setComplaint(response.data);
        setError('');
        hasLoadedComplaint = true;
        shouldPollForAnalysis = response.data.status === 'PROCESSING';
        if (shouldPollForAnalysis) {
          timeoutId = window.setTimeout(() => loadComplaint(), 2500);
        }
      } catch (requestError) {
        if (!isCurrentRequest) return;
        const status = requestError.response?.status;
        if (!hasLoadedComplaint) {
          setError(status === 404
            ? 'No report with that ID was found for your account.'
            : requestError.message || requestError.response?.data?.detail || 'Could not load this report. Please try again.');
        } else if (shouldPollForAnalysis) {
          setError('Could not refresh the analysis status. Retrying…');
          timeoutId = window.setTimeout(() => loadComplaint(), 4000);
        }
      } finally {
        if (isCurrentRequest && showLoading) setIsLoading(false);
      }
    };

    setIsLoading(true);
    setError('');
    setComplaint(null);
    loadComplaint(true);
    return () => {
      isCurrentRequest = false;
      window.clearTimeout(timeoutId);
    };
  }, [lookupId, getToken]);

  const handleSearch = (event) => {
    event.preventDefault();
    const id = complaintId.trim();
    if (!id) {
      setComplaint(null);
      setLookupId('');
      setSearchParams({});
      return;
    }
    setSearchParams({ id });
  };

  const currentStep = STATUS_STEPS.findIndex((step) => step.value === complaint?.status);
  const statusLabel = complaint?.status?.replaceAll('_', ' ').toLowerCase();
  const isAnalyzing = complaint?.status === 'PROCESSING';
  const detectionDetails = Array.isArray(complaint?.detection_details)
    ? complaint.detection_details
    : null;
  const detectionCount = detectionDetails?.length ?? Number(complaint?.detections_count ?? 0);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
          <Search className="w-3.5 h-3.5" />
          <span>Real-Time Lookup</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Track Complaint Status
        </h1>
        <p className="text-sm text-gray-400">Enter the report ID to view its current processing status and AI classification.</p>
      </div>

      {/* Search Input Card */}
      <form onSubmit={handleSearch} className="glass-panel p-6 rounded-2xl space-y-4">
        <label className="text-xs font-bold text-gray-200 uppercase tracking-wider block">
          Lookup Complaint Ticket
        </label>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="e.g. RR-2026-89421"
              value={complaintId}
              onChange={(e) => setComplaintId(e.target.value)}
              aria-label="Complaint ID"
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-blue-500 placeholder-gray-500 font-mono"
            />
          </div>
          <button type="submit" disabled={isLoading} className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white font-semibold text-sm transition-colors flex items-center justify-center gap-2 shadow-md">
            <Search className="w-4 h-4" />
            <span>Search Ticket</span>
          </button>
        </div>
      </form>

      {isLoading && (
        <div role="status" className="glass-panel p-6 rounded-2xl flex items-center gap-3 text-sm text-gray-300">
          <Loader2 className="w-5 h-5 animate-spin text-blue-400" /> Loading your report…
        </div>
      )}

      {error && (
        <div role="alert" className="glass-panel p-5 rounded-2xl flex items-start gap-3 text-sm text-red-300">
          <AlertCircle className="w-5 h-5 shrink-0" /> <span>{error}</span>
        </div>
      )}

      {complaint && (
      <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-gray-800 pb-4">
          <div className="min-w-0">
            <span className="text-xs text-gray-400 uppercase font-mono">Report #{complaint.id}</span>
            <h3 className="text-lg font-bold text-white">{complaint.ai_category || complaint.category}</h3>
            {complaint.description && <p className="mt-1 text-sm text-gray-400">{complaint.description}</p>}
          </div>
          <span className="ml-3 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs font-bold uppercase whitespace-nowrap">
            {statusLabel || 'status unavailable'}
          </span>
        </div>

        {isAnalyzing && (
          <div role="status" className="flex items-center gap-3 rounded-xl border border-blue-500/20 bg-blue-500/5 p-4 text-sm text-blue-200">
            <Loader2 className="h-5 w-5 shrink-0 animate-spin text-blue-400" />
            <div>
              <p className="font-semibold">AI is analyzing this image</p>
              <p className="text-xs text-gray-400">This report refreshes automatically while analysis is running.</p>
            </div>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl bg-gray-900/60 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">AI severity</p>
            <p className="mt-1 text-lg font-bold text-white">{complaint.severity_level}</p>
            <p className="text-xs text-gray-400">Score: {Number(complaint.severity_score || 0).toFixed(1)} / 100</p>
            <p className="mt-1 text-xs text-gray-400">
              {detectionDetails === null
                ? (isAnalyzing
                  ? 'Detection details are pending analysis'
                  : detectionCount > 0
                    ? `${detectionCount} damage region${detectionCount === 1 ? '' : 's'} detected; breakdown unavailable`
                    : 'Detection count unavailable for this report')
                : `${detectionCount} damage region${detectionCount === 1 ? '' : 's'} detected`}
            </p>
          </div>
          <div className="rounded-xl bg-gray-900/60 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">Report location</p>
            <p className="mt-1 text-sm text-white"><MapPin className="mr-1 inline h-4 w-4 text-blue-400" />{complaint.location.lat.toFixed(5)}, {complaint.location.lng.toFixed(5)}</p>
            {complaint.created_at && <p className="mt-1 text-xs text-gray-400">Submitted {new Date(complaint.created_at).toLocaleString()}</p>}
          </div>
        </div>

        {detectionDetails !== null && (
          <section aria-label="AI detected regions" className="rounded-xl border border-gray-800 bg-gray-900/40 p-4">
            <div className="flex items-center justify-between gap-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-300">Detected damage regions</h4>
              <span className="rounded-full bg-blue-500/10 px-2.5 py-1 text-xs font-semibold text-blue-300">
                {detectionCount} found
              </span>
            </div>
            {detectionDetails.length === 0 ? (
              <p className="mt-3 text-sm text-gray-400">The AI analysis did not find damage regions in this image.</p>
            ) : (
              <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                {detectionDetails.map((detection, index) => (
                  <li key={`${detection.class_id}-${index}`} className="flex items-center justify-between gap-3 rounded-lg bg-gray-950/60 px-3 py-2.5">
                    <span className="text-sm font-medium text-white">{detection.class_name}</span>
                    <span className="shrink-0 text-xs tabular-nums text-gray-400">
                      {`${(Number(detection.confidence) * 100).toFixed(1)}% confidence`}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        {complaint.image_url && <img src={complaint.image_url} alt="Evidence attached to this report" className="max-h-72 w-full rounded-xl object-cover" />}

        {/* Timeline Steps */}
        <div className="space-y-4 pt-2">
          <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider">
            Resolution Lifecycle Timeline
          </h4>

          <ol className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-800">
            {STATUS_STEPS.map((step, index) => {
              const StepIcon = step.icon;
              const isComplete = currentStep >= 0 && index <= currentStep;
              const isCurrent = step.value === complaint.status;
              return (
                <li key={step.value} className="relative flex items-start gap-4">
                  <span className={`absolute -left-6 top-0.5 w-4 h-4 rounded-full ring-4 ring-gray-900 flex items-center justify-center ${isComplete ? 'bg-blue-500' : 'bg-gray-700'}`}>
                    <StepIcon className="w-3 h-3 text-white" />
                  </span>
                  <div>
                    <p className={`text-sm font-bold ${isCurrent ? 'text-blue-300' : isComplete ? 'text-white' : 'text-gray-500'}`}>{step.label}{isCurrent ? ' · Current' : ''}</p>
                    <p className="text-xs text-gray-400">{step.detail}</p>
                  </div>
                </li>
              );
            })}
            {complaint.status === 'ESCALATED' && <li className="text-sm font-bold text-red-400"><ShieldAlert className="mr-2 inline h-4 w-4" />This report has been escalated.</li>}
          </ol>
        </div>

      </div>
      )}

    </div>
  );
}
