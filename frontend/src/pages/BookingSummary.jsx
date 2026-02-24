import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import PageWrapper from "../components/PageWrapper";
import SectionTitle from "../components/ui/SectionTitle";
import { useBooking } from "../context/BookingContext";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function BookingSummary() {
  const navigate = useNavigate();
  const { bookingData, updateBookingData } = useBooking();
  const { user, isAuthenticated } = useAuth();
  
  const [flightData, setFlightData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [passengerData, setPassengerData] = useState({
    passenger_name: user?.full_name || '',
    passenger_email: user?.email || '',
    passenger_phone: user?.phone || ''
  });

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (!isAuthenticated) return;

    // If no booking data, redirect back to flights
    if (!bookingData.booking || !bookingData.seat) {
      navigate('/flights');
      return;
    }

    // Pre-fill passenger data with user info
    setPassengerData({
      passenger_name: user?.full_name || '',
      passenger_email: user?.email || '',
      passenger_phone: user?.phone || ''
    });

    // Fetch flight details
    const fetchFlightData = async () => {
      try {
        const response = await api.get(`/flights/${bookingData.booking.flight_id}`);
        setFlightData(response.data);
      } catch (error) {
        console.error("Error fetching flight data:", error);
        // For now, use mock data if API fails
        setFlightData({
          from_city: "Mumbai",
          to_city: "Delhi", 
          departure_time: "2024-03-15T10:30:00",
          price: 5500
        });
      } finally {
        setLoading(false);
      }
    };

    fetchFlightData();
  }, [bookingData, navigate, user, isAuthenticated]);

  const handleProceedToPayment = () => {
    if (!passengerData.passenger_name || !passengerData.passenger_email || !passengerData.passenger_phone) {
      alert("Please fill in all passenger details");
      return;
    }

    // Store passenger data and navigate to payment
    updateBookingData({
      passenger: passengerData
    });

    navigate("/payment");
  };

  if (loading) {
    return (
      <PageWrapper>
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading booking details...</p>
          </div>
        </div>
      </PageWrapper>
    );
  }

  const seatNumber = bookingData.seat?.seat_number || `${bookingData.seat?.row}${bookingData.seat?.col}`;
  const route = flightData ? `${flightData.from_city} → ${flightData.to_city}` : "Loading...";
  const price = flightData?.price || bookingData.booking?.price || 0;

  return (
    <PageWrapper>
      <SectionTitle
        title="Booking Summary"
        subtitle="Review your journey details before confirmation"
      />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="min-h-[70vh] flex items-center justify-center"
      >
        <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-md transition max-w-2xl w-full">
          
          {/* Flight & Seat Details */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-blue-700 mb-6 text-center">
              Booking Summary
            </h2>

            <div className="w-16 h-1 bg-blue-200 mx-auto mb-6 rounded-full" />

            <div className="space-y-4 text-gray-700">
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="font-medium">Route</span>
                <span className="font-semibold">{route}</span>
              </div>

              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="font-medium">Seat</span>
                <span className="font-semibold">{seatNumber} ({bookingData.seat?.seat_class})</span>
              </div>

              {flightData?.departure_time && (
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="font-medium">Departure</span>
                  <span>{new Date(flightData.departure_time).toLocaleString()}</span>
                </div>
              )}

              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="font-medium">Price</span>
                <span className="font-bold text-lg">₹ {price.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Passenger Details Form */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Passenger Details</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  value={passengerData.passenger_name}
                  onChange={(e) => setPassengerData(prev => ({...prev, passenger_name: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter passenger name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address *
                </label>
                <input
                  type="email"
                  value={passengerData.passenger_email}
                  onChange={(e) => setPassengerData(prev => ({...prev, passenger_email: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter email address"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  value={passengerData.passenger_phone}
                  onChange={(e) => setPassengerData(prev => ({...prev, passenger_phone: e.target.value}))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter phone number"
                />
              </div>
            </div>
          </div>

          {/* Dharma Message */}
          <div className="mb-6 bg-blue-50 rounded-xl p-4 text-center">
            <p className="text-blue-800 text-sm italic">
              Every journey unfolds when the moment is right. Your seat is held with intention.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => navigate(-1)}
              className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-xl font-medium hover:bg-gray-300 transition"
            >
              Go Back
            </button>
            
            <button
              onClick={handleProceedToPayment}
              className="flex-1 bg-blue-600 text-white py-3 rounded-xl font-medium hover:bg-blue-700 transition"
            >
              Proceed to Payment
            </button>
          </div>
        </div>
      </motion.div>
    </PageWrapper>
  );
}