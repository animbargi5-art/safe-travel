import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function SocialBooking({ flight, onClose, className = '' }) {
  const { user } = useAuth();
  const [invitees, setInvitees] = useState([{ email: '', name: '', phone: '' }]);
  const [message, setMessage] = useState('');
  const [templates, setTemplates] = useState([]);
  const [isCreating, setIsCreating] = useState(false);
  const [socialBookings, setSocialBookings] = useState([]);
  const [showMyBookings, setShowMyBookings] = useState(false);

  useEffect(() => {
    fetchTemplates();
    fetchMySocialBookings();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/social-booking/invitation-templates');
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const fetchMySocialBookings = async () => {
    try {
      const response = await api.get('/social-booking/my-bookings');
      setSocialBookings(response.data.social_bookings);
    } catch (error) {
      console.error('Failed to fetch social bookings:', error);
    }
  };

  const addInvitee = () => {
    if (invitees.length < 10) {
      setInvitees([...invitees, { email: '', name: '', phone: '' }]);
    }
  };

  const removeInvitee = (index) => {
    if (invitees.length > 1) {
      setInvitees(invitees.filter((_, i) => i !== index));
    }
  };

  const updateInvitee = (index, field, value) => {
    const updated = [...invitees];
    updated[index][field] = value;
    setInvitees(updated);
  };

  const useTemplate = (template) => {
    const destination = flight?.to_city || '{destination}';
    const templateMessage = template.message.replace('{destination}', destination);
    setMessage(templateMessage);
  };

  const createSocialBooking = async () => {
    if (!flight) return;

    // Validate invitees
    const validInvitees = invitees.filter(inv => inv.email && inv.name);
    if (validInvitees.length === 0) {
      alert('Please add at least one invitee with email and name');
      return;
    }

    setIsCreating(true);
    try {
      const response = await api.post('/social-booking/create', {
        flight_id: flight.id,
        invitees: validInvitees.map(inv => ({
          email: inv.email,
          name: inv.name,
          phone: inv.phone || null,
          seat_preference: inv.seat_preference || 'ANY',
          special_requests: inv.special_requests || null
        })),
        message: message || null
      });

      if (response.data.success) {
        alert(`Social booking created! Invitations sent to ${response.data.invitations_sent} people.`);
        fetchMySocialBookings();
        onClose?.();
      }
    } catch (error) {
      console.error('Failed to create social booking:', error);
      alert('Failed to create social booking. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDING': 'bg-yellow-100 text-yellow-800',
      'ACCEPTED': 'bg-green-100 text-green-800',
      'COMPLETED': 'bg-blue-100 text-blue-800',
      'CANCELLED': 'bg-red-100 text-red-800',
      'EXPIRED': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (!user) {
    return (
      <div className={`text-center p-6 bg-gray-50 rounded-lg ${className}`}>
        <p className="text-gray-600">Please log in to use social booking</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-pink-500 to-purple-600 p-6 rounded-t-xl text-white">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-xl font-bold mb-2">👥 Social Booking</h3>
            <p className="text-pink-100">
              Invite friends and family to join your flight
            </p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-white hover:text-pink-200 text-2xl"
            >
              ×
            </button>
          )}
        </div>
      </div>

      <div className="p-6">
        {/* Tab Navigation */}
        <div className="flex mb-6 border-b">
          <button
            onClick={() => setShowMyBookings(false)}
            className={`px-4 py-2 font-medium ${
              !showMyBookings 
                ? 'text-purple-600 border-b-2 border-purple-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Create New
          </button>
          <button
            onClick={() => setShowMyBookings(true)}
            className={`px-4 py-2 font-medium ${
              showMyBookings 
                ? 'text-purple-600 border-b-2 border-purple-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            My Social Bookings ({socialBookings.length})
          </button>
        </div>

        {!showMyBookings ? (
          /* Create New Social Booking */
          <div>
            {/* Flight Info */}
            {flight && (
              <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-semibold text-blue-800 mb-2">Selected Flight</h4>
                <div className="text-sm text-blue-700">
                  <p><strong>Route:</strong> {flight.from_city} → {flight.to_city}</p>
                  <p><strong>Departure:</strong> {new Date(flight.departure_time).toLocaleString()}</p>
                  <p><strong>Airline:</strong> {flight.airline}</p>
                  <p><strong>Price:</strong> ${flight.price} per person</p>
                </div>
              </div>
            )}

            {/* Message Templates */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Choose a message template (optional):
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {templates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => useTemplate(template)}
                    className="text-left p-3 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-colors"
                  >
                    <div className="font-medium text-gray-800">{template.title}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      {template.message.substring(0, 60)}...
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Message */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Personal Message:
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Add a personal message to your invitation..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows={3}
              />
            </div>

            {/* Invitees */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-3">
                <label className="text-sm font-medium text-gray-700">
                  Invite Friends & Family:
                </label>
                <button
                  onClick={addInvitee}
                  disabled={invitees.length >= 10}
                  className="px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700 disabled:opacity-50"
                >
                  + Add Person
                </button>
              </div>

              <div className="space-y-3">
                {invitees.map((invitee, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="grid grid-cols-1 md:grid-cols-4 gap-3 p-3 border border-gray-200 rounded-lg"
                  >
                    <input
                      type="email"
                      placeholder="Email *"
                      value={invitee.email}
                      onChange={(e) => updateInvitee(index, 'email', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                    />
                    <input
                      type="text"
                      placeholder="Name *"
                      value={invitee.name}
                      onChange={(e) => updateInvitee(index, 'name', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                    />
                    <input
                      type="tel"
                      placeholder="Phone (optional)"
                      value={invitee.phone}
                      onChange={(e) => updateInvitee(index, 'phone', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <div className="flex items-center">
                      <select
                        value={invitee.seat_preference || 'ANY'}
                        onChange={(e) => updateInvitee(index, 'seat_preference', e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="ANY">Any Seat</option>
                        <option value="WINDOW">Window</option>
                        <option value="AISLE">Aisle</option>
                        <option value="MIDDLE">Middle</option>
                      </select>
                      {invitees.length > 1 && (
                        <button
                          onClick={() => removeInvitee(index)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          🗑️
                        </button>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Create Button */}
            <div className="flex justify-end">
              <button
                onClick={createSocialBooking}
                disabled={isCreating || !flight}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 font-medium"
              >
                {isCreating ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creating...
                  </div>
                ) : (
                  `Send Invitations (${invitees.filter(inv => inv.email && inv.name).length} people)`
                )}
              </button>
            </div>
          </div>
        ) : (
          /* My Social Bookings */
          <div>
            {socialBookings.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-4">👥</div>
                <p>No social bookings yet.</p>
                <p className="text-sm mt-2">Create your first group booking to get started!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {socialBookings.map((booking) => (
                  <motion.div
                    key={booking.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-800">
                          {booking.flight_details?.from_city} → {booking.flight_details?.to_city}
                        </h4>
                        <p className="text-sm text-gray-600">
                          {new Date(booking.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(booking.status)}`}>
                          {booking.status}
                        </span>
                        <span className="text-sm text-gray-500">
                          {booking.role === 'organizer' ? '👑 Organizer' : '👤 Invitee'}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Total Seats:</span>
                        <div className="font-medium">{booking.total_seats}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Confirmed:</span>
                        <div className="font-medium text-green-600">{booking.confirmed_seats}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Expires:</span>
                        <div className="font-medium">
                          {new Date(booking.expires_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-500">Total Cost:</span>
                        <div className="font-medium">${booking.total_cost || 0}</div>
                      </div>
                    </div>

                    {booking.role === 'organizer' && booking.status === 'PENDING' && (
                      <div className="mt-3 flex gap-2">
                        <button className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200">
                          Send Reminder
                        </button>
                        <button className="px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200">
                          Cancel Booking
                        </button>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}