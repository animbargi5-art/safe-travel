import { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import { motion } from 'framer-motion';
import api from '../services/api';

// Initialize Stripe
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'pk_test_...');

const CARD_ELEMENT_OPTIONS = {
  style: {
    base: {
      fontSize: '16px',
      color: '#424770',
      '::placeholder': {
        color: '#aab7c4',
      },
    },
    invalid: {
      color: '#9e2146',
    },
  },
};

function CheckoutForm({ bookingData, onPaymentSuccess, onPaymentError }) {
  const stripe = useStripe();
  const elements = useElements();
  
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [clientSecret, setClientSecret] = useState('');
  const [paymentIntentId, setPaymentIntentId] = useState('');

  // Create payment intent when component mounts
  useEffect(() => {
    const createPaymentIntent = async () => {
      try {
        const response = await api.post('/payment/create-intent', {
          booking_id: bookingData.booking.id,
          return_url: `${window.location.origin}/confirmation`
        });
        
        setClientSecret(response.data.client_secret);
        setPaymentIntentId(response.data.payment_intent_id);
      } catch (error) {
        console.error('Error creating payment intent:', error);
        setError('Failed to initialize payment. Please try again.');
      }
    };

    if (bookingData?.booking?.id) {
      createPaymentIntent();
    }
  }, [bookingData]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements || !clientSecret) {
      return;
    }

    setProcessing(true);
    setError(null);

    const card = elements.getElement(CardElement);

    // Confirm payment with Stripe
    const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(
      clientSecret,
      {
        payment_method: {
          card: card,
          billing_details: {
            name: bookingData.passenger?.passenger_name || '',
            email: bookingData.passenger?.passenger_email || '',
            phone: bookingData.passenger?.passenger_phone || '',
          },
        }
      }
    );

    if (stripeError) {
      setError(stripeError.message);
      setProcessing(false);
      onPaymentError?.(stripeError);
    } else if (paymentIntent.status === 'succeeded') {
      // Confirm payment on backend
      try {
        const response = await api.post('/payment/confirm', {
          payment_intent_id: paymentIntent.id,
          passenger_name: bookingData.passenger?.passenger_name,
          passenger_email: bookingData.passenger?.passenger_email,
          passenger_phone: bookingData.passenger?.passenger_phone
        });

        onPaymentSuccess?.(response.data);
      } catch (backendError) {
        console.error('Backend confirmation error:', backendError);
        setError('Payment succeeded but booking confirmation failed. Please contact support.');
        onPaymentError?.(backendError);
      }
    }

    setProcessing(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Payment Details */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-800 mb-3">Payment Details</h3>
        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex justify-between">
            <span>Flight:</span>
            <span className="font-medium">
              {bookingData.flight?.from_city} → {bookingData.flight?.to_city}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Seat:</span>
            <span className="font-medium">
              {bookingData.seat?.seat_number} ({bookingData.seat?.seat_class})
            </span>
          </div>
          <div className="flex justify-between">
            <span>Passenger:</span>
            <span className="font-medium">{bookingData.passenger?.passenger_name}</span>
          </div>
          <div className="flex justify-between border-t pt-2 mt-2">
            <span className="font-medium">Total:</span>
            <span className="font-bold text-lg">
              ${bookingData.booking?.price || bookingData.flight?.price || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Card Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Card Information
        </label>
        <div className="border border-gray-300 rounded-lg p-4 bg-white">
          <CardElement options={CARD_ELEMENT_OPTIONS} />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={!stripe || processing || !clientSecret}
        className="w-full bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {processing ? 'Processing Payment...' : `Pay $${bookingData.booking?.price || bookingData.flight?.price || 0}`}
      </button>

      {/* Security Notice */}
      <div className="text-center text-xs text-gray-500">
        <p>🔒 Your payment information is secure and encrypted</p>
        <p>Powered by Stripe</p>
      </div>
    </form>
  );
}

export default function PaymentForm({ bookingData, onPaymentSuccess, onPaymentError }) {
  return (
    <Elements stripe={stripePromise}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <CheckoutForm
          bookingData={bookingData}
          onPaymentSuccess={onPaymentSuccess}
          onPaymentError={onPaymentError}
        />
      </motion.div>
    </Elements>
  );
}