import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';

const WaitlistManager = ({ flight, onClose }) => {
  const [waitlistData, setWaitlistData] = useState({
    preferred_seat_class: 'ANY',
    preferred_seat_position: 'ANY',
    max_price: '',
    notify_email: true,
    notify_sms: false
  });
  const [loading, setLoading] = useState(false);
  const [userWaitlist, setUserWaitlist] = useState([]);
  const [flightStats, setFlightStats] = useState(null);

  useEffect(() => {
    fetchUserWaitlist();
    fetchFlightStats();
  }, []);

  const fetchUserWaitlist = async () => {
    try {
      const response = await api.get('/waitlist/my-waitlist');
      setUserWaitlist(response.data);
    } catch (error) {
      console.error('Failed to fetch waitlist:', error);
    }
  };

  const fetchFlightStats = async () => {
    try {
      const response = await api.get(`/waitlist/flight/${flight.id}/stats`);
      setFlightStats(response.data);
    } catch (error) {
      console.error('Failed to fetch flight stats:', error);
    }
  };

  const joinWaitlist = async () => {
    setLoading(true);
    try {
      const payload = {
        flight_id: flight.id,
        ...waitlistData,
        max_price: waitlistData.max_price ? parseInt(waitlistData.max_price) : null
      };

      const response = await api.post('/waitlist/join', payload);
      
      alert(`✅ Added to waitlist!\n\nPosition: ${response.data.waitlist_position}\nEstimated wait: ${response.data.estimated_wait_time}`);
      
      fetchUserWaitlist();
      fetchFlightStats();
      onClose();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to join waitlist');
    } finally {
      setLoading(false);
    }
  };

  const cancelWaitlistEntry = async (waitlistId) => {
    if (!confirm('Are you sure you want to cancel this waitlist entry?')) return;

    try {
      await api.delete(`/waitlist/${waitlistId}`);
      alert('Waitlist entry cancelled');
      fetchUserWaitlist();
    } catch (error) {
      alert('Failed to cancel waitlist entry');
    }
  };

  const currentFlightWaitlist = userWaitlist.find(w => w.flight.id === flight.id && w.status === 'ACTIVE');

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">🚂 Join Waitlist</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Flight Info */}
        <div className="bg-blue-50 rounded-xl p-4 mb-6">
          <h3 className="font-semibold text-blue-800 mb-2">Flight Details</h3>
          <p className="text-blue-700">
            {flight.from_city} → {flight.to_city}
          </p>
          <p className="text-blue-600 text-sm">
            {new Date(flight.departure_time).toLocaleString()}
          </p>
          <p className="text-blue-800 font-semibold">₹{flight.price}</p>
        </div>

        {/* Waitlist Stats */}
        {flightStats && (
          <div className="bg-yellow-50 rounded-xl p-4 mb-6">
            <h3 className="font-semibold text-yellow-800 mb-2">📊 Waitlist Stats</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-yellow-700">{flightStats.active_waitlist}</p>
                <p className="text-yellow-600 text-sm">Active Waitlist</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-yellow-700">{flightStats.total_waitlist}</p>
                <p className="text-yellow-600 text-sm">Total Requests</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-yellow-700">{flightStats.allocation_rate}%</p>
                <p className="text-yellow-600 text-sm">Success Rate</p>
              </div>
            </div>
          </div>
        )}

        {/* Current Waitlist Status */}
        {currentFlightWaitlist && (
          <div className="bg-green-50 rounded-xl p-4 mb-6">
            <h3 className="font-semibold text-green-800 mb-2">✅ You're on the waitlist!</h3>
            <p className="text-green-700">Position: #{currentFlightWaitlist.priority}</p>
            <p className="text-green-600 text-sm">
              Estimated wait: {currentFlightWaitlist.estimated_wait}
            </p>
            <button
              onClick={() => cancelWaitlistEntry(currentFlightWaitlist.id)}
              className="mt-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
            >
              Cancel Waitlist
            </button>
          </div>
        )}

        {/* Join Waitlist Form */}
        {!currentFlightWaitlist && (
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-800 mb-4">Waitlist Preferences</h3>

            {/* Seat Class Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Seat Class
              </label>
              <select
                value={waitlistData.preferred_seat_class}
                onChange={(e) => setWaitlistData({...waitlistData, preferred_seat_class: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="ANY">Any Class</option>
                <option value="ECONOMY">Economy</option>
                <option value="BUSINESS">Business</option>
                <option value="FIRST">First Class</option>
              </select>
            </div>

            {/* Seat Position Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Seat Position
              </label>
              <select
                value={waitlistData.preferred_seat_position}
                onChange={(e) => setWaitlistData({...waitlistData, preferred_seat_position: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="ANY">Any Position</option>
                <option value="WINDOW">Window</option>
                <option value="AISLE">Aisle</option>
                <option value="MIDDLE">Middle</option>
              </select>
            </div>

            {/* Maximum Price */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Price (Optional)
              </label>
              <input
                type="number"
                value={waitlistData.max_price}
                onChange={(e) => setWaitlistData({...waitlistData, max_price: e.target.value})}
                placeholder="Leave empty for no limit"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Notification Preferences */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Notification Preferences
              </label>
              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={waitlistData.notify_email}
                    onChange={(e) => setWaitlistData({...waitlistData, notify_email: e.target.checked})}
                    className="mr-2"
                  />
                  Email notifications
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={waitlistData.notify_sms}
                    onChange={(e) => setWaitlistData({...waitlistData, notify_sms: e.target.checked})}
                    className="mr-2"
                  />
                  SMS notifications
                </label>
              </div>
            </div>

            {/* How it Works */}
            <div className="bg-gray-50 rounded-xl p-4">
              <h4 className="font-semibold text-gray-800 mb-2">🚂 How Railway-Style Waitlist Works</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• You'll be added to the waitlist in order</li>
                <li>• When someone cancels, the next person gets the seat automatically</li>
                <li>• You'll get 15 minutes to confirm if a seat becomes available</li>
                <li>• Real-time notifications keep you updated</li>
                <li>• Higher success rate than traditional booking</li>
              </ul>
            </div>

            {/* Join Button */}
            <button
              onClick={joinWaitlist}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Joining Waitlist...' : '🚂 Join Waitlist'}
            </button>
          </div>
        )}

        {/* My Waitlist Entries */}
        {userWaitlist.length > 0 && (
          <div className="mt-8">
            <h3 className="font-semibold text-gray-800 mb-4">My Waitlist Entries</h3>
            <div className="space-y-3">
              {userWaitlist.map((entry) => (
                <div key={entry.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">
                        {entry.flight.from_city} → {entry.flight.to_city}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(entry.flight.departure_time).toLocaleString()}
                      </p>
                      <p className="text-sm">
                        Status: <span className={`font-medium ${
                          entry.status === 'ACTIVE' ? 'text-green-600' : 
                          entry.status === 'ALLOCATED' ? 'text-blue-600' : 'text-gray-600'
                        }`}>
                          {entry.status}
                        </span>
                      </p>
                      {entry.status === 'ACTIVE' && (
                        <p className="text-sm text-gray-600">
                          Position: #{entry.priority} • Wait: {entry.estimated_wait}
                        </p>
                      )}
                    </div>
                    {entry.status === 'ACTIVE' && (
                      <button
                        onClick={() => cancelWaitlistEntry(entry.id)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
};

export default WaitlistManager;