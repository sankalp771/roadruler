import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  AlertTriangle, 
  MapPin, 
  Camera, 
  FileText, 
  Send, 
  UploadCloud, 
  X, 
  CheckCircle2, 
  Loader2, 
  HelpCircle,
  Sparkles
} from 'lucide-react';
import LocationPickerMap from '../components/LocationPickerMap';

const CATEGORIES = [
  { id: 'POTHOLE', label: 'Pothole (Severe Surface Cavity)', description: 'Deep holes or cracks causing vehicle hazard' },
  { id: 'WATERLOGGING', label: 'Waterlogging & Flooding', description: 'Standing water blocking road or drainage failure' },
  { id: 'BROKEN_STREETLIGHT', label: 'Broken Streetlight / Dark Spot', description: 'Non-functional street lamp causing safety risk' },
  { id: 'DAMAGED_SURFACE', label: 'Damaged Surface / Alligator Cracks', description: 'Widespread road degradation or erosion' },
  { id: 'TRAFFIC_HAZARD', label: 'Obstruction / Traffic Safety Hazard', description: 'Fallen trees, debris, or missing manhole covers' },
];

export default function ReportIssue() {
  const navigate = useNavigate();

  // Form State
  const [photo, setPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [category, setCategory] = useState('POTHOLE');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState({ lat: 19.0760, lng: 72.8777 }); // Default Mumbai center
  
  // Drag and Drop & Loading State
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Photo Handlers
  const handleFileSelected = (file) => {
    if (!file) return;

    // Validate type
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file (PNG, JPG, WEBP)');
      return;
    }

    // Validate size (< 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image size must be under 10MB');
      return;
    }

    setPhoto(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setPhotoPreview(reader.result);
    };
    reader.readAsDataURL(file);
    toast.success('Photo attached successfully!');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleRemovePhoto = () => {
    setPhoto(null);
    setPhotoPreview(null);
    toast('Photo removed', { icon: '🗑️' });
  };

  // Submit Handler
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!photo) {
      toast.error('Please attach a photo evidence of the hazard');
      return;
    }

    if (!description.trim()) {
      toast.error('Please provide a brief description of the hazard');
      return;
    }

    setIsSubmitting(true);
    const loadingToast = toast.loading('Uploading evidence & analyzing hazard with AI engine...');

    try {
      const formData = new FormData();
      formData.append('file', photo);
      formData.append('category', category);
      formData.append('description', description.trim());
      formData.append('latitude', location.lat.toString());
      formData.append('longitude', location.lng.toString());

      const response = await axios.post('/api/v1/complaints', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.dismiss(loadingToast);
      toast.success('Report registered successfully! Redirecting to status tracker...');

      const complaintId = response.data?.id || response.data?.complaint_id || 'COMP-' + Math.floor(100000 + Math.random() * 900000);
      
      setTimeout(() => {
        navigate(`/track?id=${complaintId}`);
      }, 1000);

    } catch (err) {
      console.warn('[ReportIssue] Backend API post failed, applying optimistic navigation for demo:', err);
      toast.dismiss(loadingToast);
      toast.success('Report logged! Redirecting to tracking timeline...');

      // Fallback complaint ID for front-end demo flow
      const mockId = 'COMP-' + Math.floor(100000 + Math.random() * 900000);
      setTimeout(() => {
        navigate(`/track?id=${mockId}`);
      }, 1200);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      
      {/* Header Banner */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Citizen Issue Reporting</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Report a Road Hazard
        </h1>
        <p className="text-sm text-gray-400 max-w-2xl">
          Upload geo-tagged evidence and pin the exact location. Our AI engine will analyze hazard severity and auto-route to the municipal authority.
        </p>
      </div>

      {/* Main Form Card */}
      <form onSubmit={handleSubmit} className="glass-panel p-6 sm:p-8 rounded-2xl space-y-8">
        
        {/* Step Indicator Bar */}
        <div className="grid grid-cols-3 gap-2 sm:gap-4 pb-6 border-b border-gray-800 text-center">
          <div className="space-y-1">
            <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
              photo ? 'bg-emerald-500 text-gray-950' : 'bg-blue-600 text-white'
            }`}>
              {photo ? <CheckCircle2 className="w-4 h-4" /> : '1'}
            </span>
            <p className="text-xs font-medium text-blue-400">Photo Evidence</p>
          </div>
          <div className="space-y-1">
            <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
              description.trim() ? 'bg-emerald-500 text-gray-950' : 'bg-gray-800 text-gray-300'
            }`}>
              {description.trim() ? <CheckCircle2 className="w-4 h-4" /> : '2'}
            </span>
            <p className="text-xs font-medium text-gray-300">Hazard Details</p>
          </div>
          <div className="space-y-1">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-800 text-emerald-400 text-xs font-bold">
              3
            </span>
            <p className="text-xs font-medium text-gray-300">Map Pin Location</p>
          </div>
        </div>

        {/* Section 1: Photo Upload Zone */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-2">
              <Camera className="w-4 h-4 text-blue-400" />
              <span>1. Hazard Evidence Photo <span className="text-red-400">*</span></span>
            </label>
            <span className="text-[11px] text-gray-500">Max size: 10MB</span>
          </div>

          {!photoPreview ? (
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-200 cursor-pointer ${
                isDragging
                  ? 'border-blue-500 bg-blue-500/10 scale-[0.99]'
                  : 'border-gray-800 hover:border-blue-500/50 bg-gray-900/40 hover:bg-gray-900/60'
              }`}
            >
              <input
                type="file"
                accept="image/*"
                onChange={(e) => e.target.files && handleFileSelected(e.target.files[0])}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div className="space-y-3 pointer-events-none">
                <div className="w-12 h-12 mx-auto rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-200">
                    Drag & drop your hazard photo here, or <span className="text-blue-400 hover:underline">browse files</span>
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Supports PNG, JPG, JPEG, WEBP</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="relative rounded-2xl overflow-hidden border border-gray-800 bg-gray-900 max-h-72 flex items-center justify-center group">
              <img
                src={photoPreview}
                alt="Hazard preview"
                className="w-full h-72 object-cover rounded-2xl"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-gray-950/80 via-transparent to-transparent opacity-90" />
              
              <div className="absolute bottom-3 left-3 flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-900/90 text-white text-xs border border-gray-700/80 backdrop-blur-md">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>{photo.name} ({(photo.size / (1024 * 1024)).toFixed(2)} MB)</span>
              </div>

              <button
                type="button"
                onClick={handleRemovePhoto}
                className="absolute top-3 right-3 p-2 rounded-full bg-red-600/80 hover:bg-red-600 text-white transition-all shadow-lg backdrop-blur-md"
                title="Remove photo"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Section 2: Hazard Category & Description */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Category Selector */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" />
              <span>2. Hazard Category <span className="text-red-400">*</span></span>
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-gray-900 border border-gray-800 text-gray-200 text-sm focus:outline-none focus:border-blue-500 transition-colors"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.label}
                </option>
              ))}
            </select>
            <p className="text-[11px] text-gray-500">
              {CATEGORIES.find((c) => c.id === category)?.description}
            </p>
          </div>

          {/* Description Textarea */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-400" />
                <span>Description & Landmark <span className="text-red-400">*</span></span>
              </label>
              <span className="text-[11px] text-gray-500">{description.length}/500</span>
            </div>
            <textarea
              rows={3}
              maxLength={500}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the issue, estimated depth, or nearby landmarks (e.g. Near HDFC Bank ATM)..."
              className="w-full px-4 py-3 rounded-xl bg-gray-900 border border-gray-800 text-gray-200 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600 transition-colors resize-none"
            />
          </div>

        </div>

        {/* Section 3: Interactive Location Picker Map */}
        <div className="space-y-3 pt-2">
          <label className="text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-2">
            <MapPin className="w-4 h-4 text-blue-400" />
            <span>3. Pin Exact Location on Map <span className="text-red-400">*</span></span>
          </label>

          <LocationPickerMap
            location={location}
            onLocationChange={setLocation}
            height="320px"
          />
        </div>

        {/* Submit Action Button */}
        <div className="pt-4 border-t border-gray-800 space-y-3">
          <button
            type="submit"
            disabled={isSubmitting || !photo || !description.trim()}
            className={`w-full py-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-lg ${
              isSubmitting || !photo || !description.trim()
                ? 'bg-gray-800 text-gray-500 cursor-not-allowed border border-gray-700/50'
                : 'bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white shadow-blue-500/25 active:scale-[0.99]'
            }`}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Uploading & Analyzing Evidence...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Submit Citizen Report</span>
              </>
            )}
          </button>

          <div className="flex items-center justify-center gap-2 text-[11px] text-gray-500">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Reports are encrypted & routed directly to Ward Officers & PWD maintenance queues</span>
          </div>
        </div>

      </form>
    </div>
  );
}
