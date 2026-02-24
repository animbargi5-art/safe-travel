import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import PageWrapper from '../components/PageWrapper';
import SectionTitle from '../components/ui/SectionTitle';
import LoadingState from '../components/ui/LoadingState';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function GroupBooking() {
  const { flightId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const [flight, setFlight] = useState(null);
  const [passengers, setPassengers] = useState([
    { name: '', email: '', phone: '', age: '', special_requirements: '' },
    { name: '', email: '', phone: '', age: '', special_requirements: '' }
  ]);
  const [seatPreferences, setSeatPreferences] = useState('together');
  const [seatClass, setSeatClass] = useState('ECONOMY');
  const [specialRequests, setSpecialRequests] = useState('');
  const [loading, setLoading] = useState(false);
  const [availability, setAvailability] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (flightId) {
      loadFlightDetails();
      checkAvailability();
    }
  }, [flightId, isAuthenticated, passengers.length]);

  const loadFlightDetails = async () => {
    try {
      const response = await api.get(`/flights/${flightId}`);
      setFlight(response.data);
    } catch (err) {
      console.error('Failed to load flight details:', err);
      setError('Failed to load flight details');
    }
  };

  const checkAvailability = async () => {
    try {
      const response = await api.get(`/group-booking/availability/${flightId}`, {
        params: {
          passenger_count: passengers.length,
          seat_class: seatClass
        }
      });
      setAvailability(response.data);
    } catch (err) {
      console.error('Failed to check availability:', err);
    }
  };

  const addPassenger = () => {
    if (passengers.length < 10) {
      setPassengers([...passengers, { 
        name: '', email: '', phone: '', age: '', special_requirements: '' 
      }]);
    }
  };

  const removePassenger = (index) => {
    if (passengers.length > 2) {
      setPassengers(passengers.filter((_, i) => i !== index));
    }
  };

  const updatePassenger = (index, field, value) => {
    const updated = [...passengers];
    updated[index][field] = value;
    setPassengers(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate passengers
    const validPassengers = passengers.filter(p => p.name.trim() && p.email.trim());
    if (validPassengers.length < 2) {
      setError('Please provide details for at least 2 passengers');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/group-booking/create', {
        flight_id: parseInt(flightId),
        passengers: validPassengers,
        seat_preferences: seatPreferences,
        seat_class_preference: seatClass,
        special_requests: specialRequests
      });

      // Navigate to group booking confirmation
      navigate('/group-confirmation', { 
        state: { groupBooking: response.data } 
      });
      
    } catch (err) {
      console.error('Failed to create group booking:', err);
      setError(err.response?.data?.detail || 'Failed to create group booking');
    } finally {
      setLoading(false);
    }
  };

  if (!flight) {
    return (
      <PageWrapper>
        <LoadingState message="Loading flight details..." />
      </PageWrapper>
    );
  }

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-IN', {
      weekday: 'short',
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <PageWrapper>
      <SectionTitle
        title="Group Booking"
        subtitle="Book multiple seats with intelligent allocation"
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        {/* Flight Summary */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            ✈️ Flight Details
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-500">Route</div>
              <div className="font-medium">{flight.from_city} → {flight.to_city}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Departure</div>
              <div className="font-medium">{formatDateTime(flight.departure_time)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Price per person</div>
              <div className="font-medium text-green-600">₹{flight.price.toLocaleString()}</div>
            </div>
          </div>
        </div>

        {/* Availability Check */}
        {availability && (
          <div className={`rounded-xl p-4 mb-6 ${
            availability.can_accommodate 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center space-x-2">
              <span className={`text-2xl ${availability.can_accommodate ? 'text-green-600' : 'text-red-600'}`}>
                {availability.can_accommodate ? '✅' : '❌'}
              </span>
              <div>
                <div className={`font-medium ${availability.can_accommodate ? 'text-green-800' : 'text-red-800'}`}>
                  {availability.can_accommodate 
                    ? `${passengers.length} seats available` 
                    : 'Not enough seats available'
                  }
                </div>
                {availability.can_accommodate && (
                  <div className="text-sm text-gray-600">
                    {availability.can_seat_together 
                      ? '🎯 Group can be seated together' 
                      : '⚠️ Group may be split across rows'
                    }
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Group Preferences */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              🎯 Group Preferences
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seating Preference
                </label>
                <select
                  value={seatPreferences}
                  onChange={(e) => setSeatPreferences(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
                >
                  <option value="together">Keep group together</option>
                  <option value="window">Prefer window seats</option>
                  <option value="aisle">Prefer aisle seats</option>
                  <option value="mixed">Mixed preferences</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seat Class
                </label>
                <select
                  value={seatClass}
                  onChange={(e) => setSeatClass(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
                >
                  <option value="ECONOMY">Economy</option>
                  <option value="BUSINESS">Business</option>
                  <option value="FIRST">First Class</option>
                </select>
              </div>
            </div>
          </div>

          {/* Passenger Details */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                👥 Passenger Details ({passengers.length} passengers)
              </h3>
              <div className="space-x-2">
                <button
                  type="button"
                  onClick={addPassenger}
                  disabled={passengers.length >= 10}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                >
                  + Add Passenger
                </button>
              </div>
            </div>

            <div className="space-y-6">
              {passengers.map((passenger, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="font-medium text-gray-900">
                      Passenger {index + 1}
                    </h4>
                    {passengers.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removePassenger(index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Full Name *
                      </label>
                      <input
                        type="text"
                        value={passenger.name}
                        onChange={(e) => updatePassenger(index, 'name', e.target.value)}
                        className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email *
                      </label>
                      <input
                        type="email"
                        value={passenger.email}
                        onChange={(e) => updatePassenger(index, 'email', e.target.value)}
                        className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Phone
                      </label>
                      <input
                        type="tel"
                        value={passenger.phone}
                        onChange={(e) => updatePassenger(index, 'phone', e.target.value)}
                        className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Age
                      </label>
                      <input
                        type="number"
                        value={passenger.age}
                        onChange={(e) => updatePassenger(index, 'age', e.target.value)}
                        className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
                        min="0"
                        max="120"
                      />
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Special Requirements
                    </label>
                    <input
                      type="text"
                      value={passenger.special_requirements}
                      onChange={(e) => updatePassenger(index, 'special_requirements', e.target.value)}
                      placeholder="Dietary restrictions, accessibility needs, etc."
                      className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
                    />
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Special Requests */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              📝 Additional Requests
            </h3>
            <textarea
              value={specialRequests}
              onChange={(e) => setSpecialRequests(e.target.value)}
              placeholder="Any special requests for the group booking..."
              rows={3}
              className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="text-red-800">{error}</div>
            </div>
          )}

          {/* Total Price */}
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6">
            <div className="flex justify-between items-center">
              <div>
                <div className="text-lg font-semibold text-gray-900">
                  Total Price
                </div>
                <div className="text-sm text-gray-600">
                  {passengers.filter(p => p.name.trim()).length} passengers × ₹{flight.price.toLocaleString()}
                </div>
              </div>
              <div className="text-2xl font-bold text-green-600">
                ₹{(passengers.filter(p => p.name.trim()).length * flight.price).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="text-center">
            <button
              type="submit"
              disabled={loading || !availability?.can_accommodate}
              className="px-8 py-3 bg-blue-600 text-white rounded-xl text-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Group Booking...' : 'Create Group Booking'}
            </button>
          </div>
        </form>

        {/* Dharma Message */}
        <div className="text-center mt-8">
          <p className="text-gray-400 text-sm italic">
            "Traveling together creates bonds that last beyond the journey. May your group find harmony in both seating and spirit."
          </p>
        </div>
      </motion.div>
    </PageWrapper>
  );
}