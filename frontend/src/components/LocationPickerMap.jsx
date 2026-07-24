import React, { useState, useMemo, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { Navigation, MapPin, CheckCircle2, Compass } from 'lucide-react';
import toast from 'react-hot-toast';

// Custom Leaflet Pin Icon (SVG rendered via divIcon for reliable rendering & zero broken asset paths)
const customPinIcon = L.divIcon({
  className: 'custom-map-pin',
  html: `
    <div style="
      position: relative;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
      border: 2.5px solid #FFFFFF;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      box-shadow: 0 4px 14px rgba(59, 130, 246, 0.5);
    ">
      <div style="
        width: 10px;
        height: 10px;
        background-color: #FFFFFF;
        border-radius: 50%;
        transform: rotate(45deg);
      "></div>
    </div>
  `,
  iconSize: [36, 36],
  iconAnchor: [18, 36],
  popupAnchor: [0, -36],
});

// Helper component to handle map clicks & center updates
function MapEventsHandler({ position, onPositionChange }) {
  const map = useMap();

  useMapEvents({
    click(e) {
      const newPos = {
        lat: parseFloat(e.latlng.lat.toFixed(6)),
        lng: parseFloat(e.latlng.lng.toFixed(6)),
      };
      onPositionChange(newPos);
      map.flyTo([newPos.lat, newPos.lng], map.getZoom(), { animate: true });
    },
  });

  return null;
}

// Controller component for programmatic panning
function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center && center.lat && center.lng) {
      map.flyTo([center.lat, center.lng], 15, { animate: true, duration: 1.2 });
    }
  }, [center, map]);
  return null;
}

export default function LocationPickerMap({
  location = { lat: 19.0760, lng: 72.8777 },
  onLocationChange,
  height = '320px',
}) {
  const [locating, setLocating] = useState(false);
  const markerRef = useRef(null);

  const eventHandlers = useMemo(
    () => ({
      dragend() {
        const marker = markerRef.current;
        if (marker != null) {
          const latLng = marker.getLatLng();
          const newPos = {
            lat: parseFloat(latLng.lat.toFixed(6)),
            lng: parseFloat(latLng.lng.toFixed(6)),
          };
          onLocationChange(newPos);
          console.log(`[LocationPickerMap] Marker dragged to:`, newPos);
        }
      },
    }),
    [onLocationChange]
  );

  const handleLocateMe = (e) => {
    e.preventDefault();
    if (!navigator.geolocation) {
      toast.error('Geolocation is not supported by your browser');
      return;
    }

    setLocating(true);
    toast.loading('Acquiring your precise GPS coordinates...', { id: 'geo-locate' });

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const newPos = {
          lat: parseFloat(pos.coords.latitude.toFixed(6)),
          lng: parseFloat(pos.coords.longitude.toFixed(6)),
        };
        onLocationChange(newPos);
        setLocating(false);
        toast.success(`Location acquired! (${newPos.lat}, ${newPos.lng})`, { id: 'geo-locate' });
        console.log(`[LocationPickerMap] Geolocation acquired:`, newPos);
      },
      (err) => {
        setLocating(false);
        toast.error(`Failed to get location: ${err.message}`, { id: 'geo-locate' });
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  return (
    <div className="space-y-3">
      {/* Map Container */}
      <div 
        className="relative rounded-2xl overflow-hidden border border-gray-800 shadow-xl bg-gray-950"
        style={{ height }}
      >
        <MapContainer
          center={[location.lat, location.lng]}
          zoom={13}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%', zIndex: 10 }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapEventsHandler position={location} onPositionChange={onLocationChange} />
          <MapRecenter center={location} />

          <Marker
            draggable={true}
            eventHandlers={eventHandlers}
            position={[location.lat, location.lng]}
            ref={markerRef}
            icon={customPinIcon}
          >
            <Popup className="dark-popup">
              <div className="p-1 text-center font-sans">
                <p className="text-xs font-bold text-gray-900">Selected Location</p>
                <p className="text-[11px] text-gray-600 font-mono">
                  {location.lat.toFixed(6)}, {location.lng.toFixed(6)}
                </p>
                <p className="text-[10px] text-blue-600 font-medium mt-1">Drag marker or click map to move</p>
              </div>
            </Popup>
          </Marker>
        </MapContainer>

        {/* Floating Locate Me Button */}
        <button
          type="button"
          onClick={handleLocateMe}
          disabled={locating}
          className="absolute top-4 right-4 z-[400] flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gray-900/90 hover:bg-gray-800 text-white font-medium text-xs border border-gray-700/80 shadow-lg backdrop-blur-md transition-all active:scale-95 disabled:opacity-50"
          title="Use my current GPS position"
        >
          <Navigation className={`w-3.5 h-3.5 text-blue-400 ${locating ? 'animate-spin' : ''}`} />
          <span>{locating ? 'Locating...' : 'Locate Me'}</span>
        </button>

        {/* Overlay Instruction Badge */}
        <div className="absolute bottom-4 left-4 z-[400] pointer-events-none hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-950/80 text-gray-300 text-[11px] border border-gray-800/80 backdrop-blur-sm shadow-md">
          <Compass className="w-3.5 h-3.5 text-blue-400" />
          <span>Click map or drag marker to set exact location</span>
        </div>
      </div>

      {/* Coordinate Display Footer */}
      <div className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-gray-900/60 border border-gray-800 text-xs">
        <div className="flex items-center gap-2 text-gray-400 font-mono">
          <MapPin className="w-4 h-4 text-blue-400" />
          <span>Lat: <strong className="text-white">{location.lat.toFixed(6)}</strong></span>
          <span className="text-gray-600">|</span>
          <span>Lng: <strong className="text-white">{location.lng.toFixed(6)}</strong></span>
        </div>
        <div className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>6-Decimal Precision</span>
        </div>
      </div>
    </div>
  );
}
