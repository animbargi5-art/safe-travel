import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import PageWrapper from "../components/PageWrapper";
import SectionTitle from "../components/ui/SectionTitle";
import { useBooking } from "../context/BookingContext";

export default function Confirmation() {
  const navigate = useNavigate();
  const { bookingData, clearBookingData } = useBooking();

  useEffect(() => {
    // If no confirmed booking, redirect to home
    if (!bookingData.booking || bookingData.booking.status !== 'CONFIRMED') {
      navigate('/');
      return;
    }
  }, [bookingData, navigate]);

  const handleViewBookings = () => {
    clearBookingData(); // Clear the booking context
    navigate("/bookings");
  };

  const handleBackHome = () => {
    clearBookingData(); // Clear the booking context
    navigate("/");
  };

  if (!bookingData.booking) {
    return null; // Will redirect in useEffect
  }

  const seatNumber = bookingData.seat?.seat_number || `${bookingData.seat?.row}${bookingData.seat?.col}`;
  const bookingId = bookingData.booking?.id;

  return (
    <PageWrapper>
      <SectionTitle
        title="Booking Confirmed"
        subtitle="Your journey awaits with perfect timing"
      />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="min-h-[70vh] flex items-center justify-center"
      >
        <div className="bg-white p-12 rounded-2xl shadow-sm hover:shadow-md transition text-center max-w-lg w-full">
          
          {/* Success Icon */}
          <div className="w-20 h-20 mx-auto mb-6 flex items-center justify-center rounded-full bg-green-100">
            <span className="text-3xl">✈️</span>
          </div>

          {/* Title */}
          <h2 className="text-3xl font-bold text-green-700 mb-4">
            Booking Confirmed!
          </h2>

          {/* Divider */}
          <div className="w-16 h-1 bg-green-200 mx-auto mb-6 rounded-full" />

          {/* Booking Details */}
          <div className="bg-gray-50 rounded-xl p-6 mb-6 text-left">
            <h3 className="font-semibold text-gray-800 mb-3">Booking Details</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Booking ID:</span>
                <span className="font-mono font-medium">#{bookingId}</span>
              </div>
              <div className="flex justify-between">
                <span>Passenger:</span>
                <span className="font-medium">{bookingData.passenger?.passenger_name}</span>
              </div>
              <div className="flex justify-between">
                <span>Seat:</span>
                <span className="font-medium">{seatNumber} ({bookingData.seat?.seat_class})</span>
              </div>
              <div className="flex justify-between">
                <span>Email:</span>
                <span className="font-medium">{bookingData.passenger?.passenger_email}</span>
              </div>
            </div>
          </div>

          {/* Message */}
          <p className="text-gray-600 leading-relaxed mb-6">
            Your journey has been successfully booked. A confirmation email has been sent to your registered email address.
          </p>

          {/* Calm Quote */}
          <div className="bg-green-50 rounded-xl p-4 mb-8">
            <p className="text-green-800 text-sm italic">
              When actions align with dharma, the path becomes clear and the journey unfolds with grace.
            </p>
          </div>

          {/* Actions */}
          <div className="flex flex-col gap-3">
            <button
              onClick={handleViewBookings}
              className="w-full bg-green-600 text-white py-3 rounded-xl font-medium hover:bg-green-700 transition"
            >
              View My Bookings
            </button>

            <button
              onClick={handleBackHome}
              className="w-full border border-gray-300 py-3 rounded-xl text-gray-600 hover:bg-gray-50 transition"
            >
              Book Another Flight
            </button>
          </div>
        </div>
      </motion.div>
    </PageWrapper>
  );
}