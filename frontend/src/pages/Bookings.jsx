import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import PageWrapper from "../components/PageWrapper";
import SectionTitle from "../components/ui/SectionTitle";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function Bookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchBookings = async () => {
      try {
        const response = await api.get('/booking/my-bookings');
        setBookings(response.data);
      } catch (error) {
        console.error("Error fetching bookings:", error);
        setBookings([]); // Show empty state on error
      } finally {
        setLoading(false);
      }
    };

    fetchBookings();
  }, [isAuthenticated]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'CONFIRMED': return 'bg-green-100 text-green-800';
      case 'HOLD': return 'bg-yellow-100 text-yellow-800';
      case 'EXPIRED': return 'bg-red-100 text-red-800';
      case 'CANCELLED': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <PageWrapper>
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading your bookings...</p>
          </div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <SectionTitle
        title="My Bookings"
        subtitle="Your journey history and upcoming travels"
      />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="min-h-[70vh]"
      >
        <div className="max-w-4xl mx-auto">
          
          {bookings.length === 0 ? (
            /* Empty State */
            <div className="bg-white rounded-2xl p-12 shadow-sm text-center">
              <div className="w-20 h-20 mx-auto mb-6 flex items-center justify-center rounded-full bg-blue-100">
                <span className="text-3xl">✈️</span>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-4">
                No Bookings Yet
              </h3>
              
              <p className="text-gray-500 text-lg mb-6">
                Your past and upcoming journeys will appear here.
              </p>

              <p className="text-sm text-gray-400 mb-8">
                Every journey begins with a single step — in perfect timing.
              </p>

              <button
                onClick={() => window.location.href = '/search'}
                className="bg-blue-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-blue-700 transition"
              >
                Book Your First Flight
              </button>

              {/* Dharma reflection */}
              <div className="mt-8 p-4 bg-blue-50 rounded-xl">
                <p className="text-blue-800 italic text-sm">
                  "Everything happens in due course of time, when dharma aligns with action."
                </p>
              </div>
            </div>
          ) : (
            /* Bookings List */
            <div className="space-y-4">
              {bookings.map((booking) => (
                <motion.div
                  key={booking.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                  className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-lg font-semibold text-gray-800">
                          Booking #{booking.id}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(booking.status)}`}>
                          {booking.status}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium text-gray-800">Route:</span>
                          <p>{booking.flight?.from_city} → {booking.flight?.to_city}</p>
                        </div>
                        
                        <div>
                          <span className="font-medium text-gray-800">Seat:</span>
                          <p>{booking.seat?.seat_number} ({booking.seat?.seat_class})</p>
                        </div>
                        
                        <div>
                          <span className="font-medium text-gray-800">Passenger:</span>
                          <p>{booking.passenger_name || 'Not provided'}</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3 text-sm text-gray-600">
                        <div>
                          <span className="font-medium text-gray-800">Departure:</span>
                          <p>{booking.flight?.departure_time ? formatDate(booking.flight.departure_time) : 'TBD'}</p>
                        </div>
                        
                        <div>
                          <span className="font-medium text-gray-800">Booked:</span>
                          <p>{formatDate(booking.created_at)}</p>
                        </div>
                        
                        <div>
                          <span className="font-medium text-gray-800">Price:</span>
                          <p className="font-semibold">₹ {booking.price?.toLocaleString() || 'N/A'}</p>
                        </div>
                      </div>

                      {booking.status === 'HOLD' && booking.expires_at && (
                        <div className="mt-3 p-3 bg-yellow-50 rounded-lg">
                          <p className="text-yellow-800 text-sm">
                            <span className="font-medium">Hold expires:</span> {formatDate(booking.expires_at)}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </PageWrapper>
  );
}