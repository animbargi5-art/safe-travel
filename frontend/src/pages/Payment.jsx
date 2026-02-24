import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { motion } from 'framer-motion';
import PageWrapper from '../components/PageWrapper';
import SectionTitle from '../components/ui/SectionTitle';
import PaymentForm from '../components/PaymentForm';
import { useBooking } from '../context/BookingContext';
import { useAuth } from '../context/AuthContext';

export default function Payment() {
  const navigate = useNavigate();
  const { bookingData, updateBookingData } = useBooking();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    // Redirect if not authenticated
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    // Redirect if no booking data
    if (!bookingData.booking || !bookingData.seat || !bookingData.passenger) {
      navigate('/flights');
      return;
    }
  }, [isAuthenticated, bookingData, navigate]);

  const handlePaymentSuccess = (paymentResult) => {
    // Update booking data with confirmed booking
    updateBookingData({
      booking: paymentResult.booking,
      payment: paymentResult.payment
    });

    // Navigate to confirmation page
    navigate('/confirmation');
  };

  const handlePaymentError = (error) => {
    console.error('Payment error:', error);
    // Could show a more detailed error page or modal
  };

  if (!bookingData.booking) {
    return null; // Will redirect in useEffect
  }

  return (
    <PageWrapper>
      <SectionTitle
        title="Complete Your Payment"
        subtitle="Secure your journey with dharma-aligned intention"
      />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="min-h-[70vh] flex items-center justify-center"
      >
        <div className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-md transition max-w-lg w-full">
          
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center rounded-full bg-green-100">
              <span className="text-2xl">💳</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-800">Secure Payment</h2>
            <p className="text-gray-600 mt-2">Complete your booking with confidence</p>
          </div>

          {/* Payment Form */}
          <PaymentForm
            bookingData={bookingData}
            onPaymentSuccess={handlePaymentSuccess}
            onPaymentError={handlePaymentError}
          />

          {/* Dharma Message */}
          <div className="mt-8 p-4 bg-green-50 rounded-lg text-center">
            <p className="text-green-800 text-sm italic">
              "When intention aligns with action, abundance flows naturally and the path becomes clear."
            </p>
          </div>
        </div>
      </motion.div>
    </PageWrapper>
  );
}