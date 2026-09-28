import React from 'react';
import { ArrowRight, Heart, X } from 'lucide-react';

export default function DuplicateWarningModal({
  photoPreview,
  complaint,
  isUpvoting,
  onUpvote,
  onFileSeparate,
  onClose,
}) {
  if (!complaint) return null;

  return (
    <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-gray-950/85 p-4 backdrop-blur-sm" role="presentation">
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="duplicate-warning-title"
        className="relative w-full max-w-2xl space-y-5 rounded-2xl border border-yellow-500/30 bg-gray-950 p-5 shadow-2xl sm:p-7"
      >
        <button
          type="button"
          onClick={onClose}
          aria-label="Close duplicate warning"
          className="absolute right-4 top-4 rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white"
        >
          <X className="h-4 w-4" />
        </button>
        <div className="space-y-1 pr-10">
          <p className="text-xs font-bold uppercase tracking-widest text-yellow-400">Nearby report found</p>
          <h2 id="duplicate-warning-title" className="text-xl font-bold text-white">Is this the same road issue?</h2>
          <p className="text-sm text-gray-400">A report is already open {Math.round(complaint.distance_meters)} meters from your pin. Supporting it helps keep reports together.</p>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:gap-5">
          <figure className="space-y-2">
            <img src={photoPreview} alt="Your selected road issue photo" className="h-36 w-full rounded-xl border border-gray-800 object-cover sm:h-48" />
            <figcaption className="text-xs font-semibold text-gray-300">Your photo</figcaption>
          </figure>
          <figure className="space-y-2">
            <img src={complaint.image_url} alt="Photo on the nearby report" className="h-36 w-full rounded-xl border border-gray-800 object-cover sm:h-48" />
            <figcaption className="truncate text-xs font-semibold text-gray-300">Existing: {complaint.ai_category || complaint.category}</figcaption>
          </figure>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={onUpvote}
            disabled={isUpvoting}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-yellow-500 px-4 py-3 text-sm font-bold text-gray-950 transition hover:bg-yellow-400 disabled:cursor-wait disabled:opacity-60"
          >
            <Heart className="h-4 w-4" />
            {isUpvoting ? 'Supporting…' : 'Upvote & Support Existing Ticket'}
          </button>
          <button
            type="button"
            onClick={onFileSeparate}
            disabled={isUpvoting}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-gray-700 px-4 py-3 text-sm font-semibold text-gray-200 transition hover:border-gray-500 hover:bg-gray-900 disabled:opacity-60"
          >
            File as a separate issue <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </section>
    </div>
  );
}
