import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import PageWrapper from '../components/PageWrapper';
import SectionTitle from '../components/ui/SectionTitle';
import api from '../services/api';

export default function GroupConfirmation() {
  const location = useLocation();
  const navigate = useNavigate();
  const [groupBooking, setGroupBooking] = useState(null);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    if (location.state?.groupBooking) {
      setGroupBooking(location.state.groupBooking);
    } else {
      navigate('/');
    }
  }, [location.state, navigate]);

  const handleConfirm = async () => {
    if (!groupBooking) return;

    setConfirming(true);
    try {
      await api.post(`/group-booking/confirm/${groupBooking.group_booking_id}`);
      
      // Navigate to payment or final confirmation
      navigate('/bookings', { 
        state: { 
          message: 'Group booking confirmed successfully!',
          groupBookingId: groupBooking.group_booking_id
        }
      });
    } catch (err) {
      console.error('Failed to confirm group booking:', err);
      alert('Failed to confirm group booking. Please try again.');
    } finally {
      setConfirming(false);
    }
  };

  const handleCancel = async () => {
    if (!groupBooking) return;

    if (confirm('Are you sure you want to cancel this group booking?')) {
      try {
        await api.delete(`/group-booking/cancel/${groupBooking.group_booking_id}`);
        navigate('/flights', { 
          state: { message: 'Group booking cancelled.' }
        });
      } catch (err) {
        console.error('Failed to cancel group booking:', err);
        alert('Failed to cancel group booking. Please try again.');
      }
    }
  };

  if (!groupBooking) {
    return (
      <PageWrapper>
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔄</div>
          <div className="text-xl text-gray-600">Loading group booking details...</div>
        </div>
      </PageWrapper>
    );
  }

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-IN', {
      weekday: 'long',
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const timeUntilExpiry = () => {
    const now = new Date();
    const expiry = new Date(groupBooking.expires_at);
    const diff = expiry - now;
    
    if (diff <= 0) return 'Expired';
    
    const minutes = Math.floor(diff / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <PageWrapper>
      <SectionTitle
        title="Group Booking Created"
        subtitle="Review and confirm your group booking"
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        {/* Success Message */}
        <div className="bg-green-50 border border-green-200 rounded-xl p-6 mb-8">
          <div className="flex items-center space-x-3">
            <div className="text-3xl text-green-600">🎉</div>
            <div>
              <div className="text-lg font-semibold text-green-800">
                Group Booking Created Successfully!
              </div>
              <div className="text-green-700">
                Booking ID: <span className="font-mono font-medium">{groupBooking.group_booking_id}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Expiry Timer */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-yellow-600">⏰</span>
              <span className="text-yellow-800 font-medium">
                Booking expires in: {timeUntilExpiry()}
              </span>
            </div>
            <div className="text-sm text-yellow-700">
              Please confirm your booking before it expires
            </div>
          </div>
        </div>

        {/* Booking Summary */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            📋 Booking Summary
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <div className="text-sm text-gray-500">Group Size</div>
              <div className="text-lg font-medium">{groupBooking.individual_bookings.length} passengers</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Total Price</div>
              <div className="text-lg font-medium text-green-600">₹{groupBooking.total_price.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Status</div>
              <div className="text-lg font-medium">
                <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-sm">
                  {groupBooking.status}
                </span>
              </div>
            </div>
          </div>

          {/* Seat Allocation */}
          <div className="border-t pt-6">
            <h4 className="font-semibold text-gray-900 mb-3">🎯 Seat Allocation</h4>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-sm text-blue-700 mb-2">Allocated Seats:</div>
              <div className="flex flex-wrap gap-2">
                {groupBooking.seats_allocated.map((seat, index) => (
                  <span
                    key={index}
                    className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium"
                  >
                    {seat}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Passenger Details */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            👥 Passenger Details
          </h3>
          
          <div className="space-y-4">
            {groupBooking.individual_bookings.map((booking, index) => (
              <div key={index} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">{booking.passenger_name}</div>
                  <div className="text-sm text-gray-600">Booking #{booking.booking_id}</div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-blue-600">{booking.seat_number}</div>
                  <div className="text-sm text-gray-600">₹{booking.price.toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={handleConfirm}
            disabled={confirming}
            className="px-8 py-3 bg-green-600 text-white rounded-xl text-lg font-medium hover:bg-green-700 transition disabled:opacity-50"
          >
            {confirming ? 'Confirming...' : '✅ Confirm Group Booking'}
          </button>
          
          <button
            onClick={handleCancel}
            className="px-8 py-3 border border-gray-300 text-gray-700 rounded-xl text-lg font-medium hover:bg-gray-50 transition"
          >
            ❌ Cancel Booking
          </button>
        </div>

        {/* Important Notes */}
        <div className="bg-blue-50 rounded-xl p-6 mt-8">
          <h4 className="font-semibold text-blue-900 mb-3">📌 Important Notes</h4>
          <ul className="space-y-2 text-blue-800 text-sm">
            <li>• Your group booking will expire in 15 minutes if not confirmed</li>
            <li>• All passengers in the group will receive individual booking confirmations</li>
            <li>• Seat assignments are optimized to keep your group together when possible</li>
            <li>• Changes to individual bookings may affect the entire group</li>
            <li>• Payment will be processed after confirmation</li>
          </ul>
        </div>

        {/* Dharma Message */}
        <div className="text-center mt-8">
          <p className="text-gray-400 text-sm italic">
            "A journey shared is a journey multiplied. May your group travel with unity and joy."
          </p>
        </div>
      </motion.div>
    </PageWrapper>
  );
}