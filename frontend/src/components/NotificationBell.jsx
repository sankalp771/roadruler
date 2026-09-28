import React, { useCallback, useEffect, useState } from 'react';
import { Bell, Check, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

export default function NotificationBell() {
  const { isSignedIn, user, getToken } = useAuth();
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const enabled = isSignedIn && !user?.isDemo;

  const refresh = useCallback(async () => {
    if (!enabled) return;
    setLoading(true);
    try {
      const token = await getToken();
      if (!token) throw new Error('Authentication token unavailable');
      const { data } = await axios.get('/api/v1/notifications?limit=20', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setItems(data.items);
      setUnreadCount(data.unread_count);
      setError('');
    } catch {
      setError('Notifications could not be loaded.');
    } finally {
      setLoading(false);
    }
  }, [enabled, getToken]);

  useEffect(() => {
    if (!enabled) return undefined;
    refresh();
    const timer = window.setInterval(refresh, 60_000);
    return () => window.clearInterval(timer);
  }, [enabled, refresh]);

  const markRead = async (notificationId) => {
    try {
      const token = await getToken();
      await axios.post(`/api/v1/notifications/${encodeURIComponent(notificationId)}/read`, null, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setItems((current) => current.map((item) => item.id === notificationId ? { ...item, is_read: true } : item));
      setUnreadCount((count) => Math.max(0, count - 1));
    } catch {
      setError('This notification could not be marked as read.');
    }
  };

  if (!enabled) return null;

  return (
    <div className="relative">
      <button
        type="button"
        aria-label={`Notifications${unreadCount ? `, ${unreadCount} unread` : ''}`}
        aria-expanded={open}
        onClick={() => { setOpen((value) => !value); if (!open) refresh(); }}
        className="relative p-2 rounded-lg text-gray-300 hover:text-white hover:bg-gray-800/70 border border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && <span className="absolute -top-1 -right-1 min-w-5 h-5 px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center">{unreadCount > 99 ? '99+' : unreadCount}</span>}
      </button>

      {open && (
        <section aria-label="Notifications" className="absolute right-0 mt-2 w-[min(24rem,calc(100vw-2rem))] glass-panel rounded-xl border border-gray-700 shadow-2xl z-[60] overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
            <div>
              <h2 className="text-sm font-bold text-white">Notifications</h2>
              <p className="text-[11px] text-gray-400">{unreadCount} unread</p>
            </div>
            <button type="button" aria-label="Refresh notifications" onClick={refresh} className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
          {error && <p role="status" className="px-4 py-3 text-xs text-amber-300">{error}</p>}
          <div className="max-h-96 overflow-y-auto divide-y divide-gray-800/80">
            {!loading && items.length === 0 && !error && <p className="px-4 py-6 text-center text-xs text-gray-400">You’re all caught up.</p>}
            {items.map((item) => (
              <article key={item.id} className={`px-4 py-3 flex items-start gap-3 ${item.is_read ? 'opacity-65' : 'bg-blue-500/5'}`}>
                <div className={`mt-1 w-2 h-2 rounded-full shrink-0 ${item.is_read ? 'bg-gray-600' : 'bg-blue-400'}`} />
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-gray-200 leading-relaxed">{item.message}</p>
                  <p className="mt-1 text-[10px] text-gray-500">{new Date(item.created_at).toLocaleString()} · Report {item.complaint_id}</p>
                </div>
                {!item.is_read && <button type="button" aria-label="Mark notification as read" onClick={() => markRead(item.id)} className="p-1.5 rounded-md text-gray-400 hover:text-emerald-300 hover:bg-gray-800"><Check className="w-4 h-4" /></button>}
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
