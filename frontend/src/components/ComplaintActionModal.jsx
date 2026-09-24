import { useState } from 'react';
import axios from 'axios';
import { LoaderCircle, Upload, X } from 'lucide-react';

const NEXT_STATUS = {
  RECEIVED: 'ASSIGNED',
  ASSIGNED: 'IN_REPAIR',
  IN_REPAIR: 'RESOLVED',
};

export default function ComplaintActionModal({ complaint, getToken, onClose, onUpdated }) {
  const [nextStatus, setNextStatus] = useState(NEXT_STATUS[complaint.status] || '');
  const [contractor, setContractor] = useState('');
  const [notes, setNotes] = useState('');
  const [resolutionImage, setResolutionImage] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const allowedNextStatus = NEXT_STATUS[complaint.status];

  async function submit(event) {
    event.preventDefault();
    if (!allowedNextStatus || nextStatus !== allowedNextStatus) {
      setError('This complaint cannot move to the selected status from its current state.');
      return;
    }
    if (nextStatus === 'RESOLVED' && !resolutionImage) {
      setError('Add a resolution photo before closing this complaint.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const token = await getToken();
      if (!token) throw new Error('A Clerk authority session is required to update complaints.');
      const headers = { Authorization: `Bearer ${token}` };
      let resolutionImageUrl;
      if (resolutionImage) {
        const formData = new FormData();
        formData.append('file', resolutionImage);
        const uploadResponse = await axios.post(
          `/api/v1/authority/complaints/${complaint.id}/resolution-image`,
          formData,
          { headers },
        );
        resolutionImageUrl = uploadResponse.data.resolution_image_url;
      }
      await axios.patch(`/api/v1/authority/complaints/${complaint.id}/status`, {
        status: nextStatus,
        contractor_name: contractor.trim() || null,
        notes: notes.trim() || null,
        resolution_image_url: resolutionImageUrl || null,
      }, { headers });
      await onUpdated();
      onClose();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || requestError.message || 'Could not update this complaint.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-gray-950/80 p-4 backdrop-blur-sm" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget && !saving) onClose(); }}>
      <section role="dialog" aria-modal="true" aria-labelledby="complaint-action-title" className="w-full max-w-xl space-y-5 rounded-2xl border border-gray-700 bg-gray-900 p-5 shadow-2xl sm:p-6">
        <header className="flex items-start justify-between gap-4">
          <div><h2 id="complaint-action-title" className="text-lg font-bold text-white">Update complaint</h2><p className="mt-1 text-xs text-gray-400">{complaint.ai_category || complaint.category} · {complaint.id}</p></div>
          <button type="button" aria-label="Close dialog" onClick={onClose} disabled={saving} className="rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white"><X className="h-5 w-5" /></button>
        </header>
        {allowedNextStatus ? <form onSubmit={submit} className="space-y-4">
          <label className="block space-y-1.5 text-xs font-medium text-gray-300">Next status
            <select required value={nextStatus} onChange={(event) => setNextStatus(event.target.value)} className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2.5 text-sm text-white">
              <option value={allowedNextStatus}>{allowedNextStatus.replace('_', ' ')}</option>
            </select>
          </label>
          <label className="block space-y-1.5 text-xs font-medium text-gray-300">Contractor name (optional)
            <input maxLength={120} value={contractor} onChange={(event) => setContractor(event.target.value)} className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2.5 text-sm text-white" placeholder="Assigned repair contractor" />
          </label>
          <label className="block space-y-1.5 text-xs font-medium text-gray-300">Officer notes (optional)
            <textarea maxLength={2000} rows={3} value={notes} onChange={(event) => setNotes(event.target.value)} className="w-full resize-y rounded-lg border border-gray-700 bg-gray-950 px-3 py-2.5 text-sm text-white" placeholder="Work order notes or progress update" />
          </label>
          {nextStatus === 'RESOLVED' && <label className="block space-y-2 text-xs font-medium text-gray-300">Resolution photo (required)
            <span className="flex items-center gap-2 rounded-lg border border-dashed border-gray-600 bg-gray-950 px-3 py-3 text-sm text-gray-300"><Upload className="h-4 w-4 text-blue-400" /><input required type="file" accept="image/jpeg,image/png,image/webp" onChange={(event) => setResolutionImage(event.target.files?.[0] || null)} className="min-w-0 flex-1 text-xs file:mr-3 file:rounded-md file:border-0 file:bg-gray-800 file:px-2 file:py-1 file:text-gray-200" /></span>
          </label>}
          {error && <p role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">{error}</p>}
          <footer className="flex justify-end gap-2 border-t border-gray-800 pt-4"><button type="button" disabled={saving} onClick={onClose} className="rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-300">Cancel</button><button disabled={saving} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-60">{saving && <LoaderCircle className="h-4 w-4 animate-spin" />}{saving ? 'Saving…' : 'Save update'}</button></footer>
        </form> : <div className="space-y-4"><p className="rounded-lg border border-gray-700 bg-gray-950 p-4 text-sm text-gray-300">This complaint is currently <strong className="text-white">{complaint.status}</strong> and has no available next action.</p><div className="flex justify-end"><button onClick={onClose} className="rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-300">Close</button></div></div>}
      </section>
    </div>
  );
}
