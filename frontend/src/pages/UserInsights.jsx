import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Layout from '../components/Layout';
import LoadingState from '../components/ui/LoadingState';
import Card from '../components/ui/Card';
import SectionTitle from '../components/ui/SectionTitle';

const UserInsights = () => {
  const { user } = useAuth();
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user) {
      fetchUserInsights();
    }
  }, [user]);

  const fetchUserInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/ml/analytics/user-insights');
      setInsights(response.data.insights);
    } catch (err) {
      console.error('Error fetching user insights:', err);
      setError('Failed to load your travel insights');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Analyzing your travel patterns..." />;
  if (error) return (
    <Layout>
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error}</div>
        <button 
          onClick={fetchUserInsights}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    </Layout>
  );

  if (!insights) return null;

  const { preferences, recommended_flights, data_points } = insights;

  return (
    <Layout>
      <div className="max-w-6xl mx-auto px-4 py-8">
        <SectionTitle 
          title="Your Travel Insights" 
          subtitle="AI-powered analysis of your booking patterns and preferences"
        />

        {/* Travel Preferences */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                🎯 Your Travel Preferences
              </h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Preferred Times</h4>
                  <div className="flex flex-wrap gap-2">
                    {preferences.preferred_times.map((time, index) => (
                      <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                        {time.charAt(0).toUpperCase() + time.slice(1)}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Seat Preferences</h4>
                  <div className="flex flex-wrap gap-2">
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                      {preferences.preferred_seat_class}
                    </span>
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                      {preferences.preferred_seat_position}
                    </span>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Price Sensitivity</h4>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    preferences.price_sensitivity === 'high' ? 'bg-red-100 text-red-800' :
                    preferences.price_sensitivity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-purple-100 text-purple-800'
                  }`}>
                    {preferences.price_sensitivity.charAt(0).toUpperCase() + preferences.price_sensitivity.slice(1)} sensitivity
                  </span>
                </div>

                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Booking Pattern</h4>
                  <p className="text-sm text-gray-600">
                    You typically book {preferences.booking_patterns.advance_days} days in advance
                  </p>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                ✈️ Favorite Routes
              </h3>
              
              {preferences.preferred_routes.length > 0 ? (
                <div className="space-y-3">
                  {preferences.preferred_routes.map((route, index) => (
                    <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="font-medium text-gray-900">{route.route}</span>
                      <div className="text-right">
                        <div className="text-sm text-gray-600">{route.frequency} trips</div>
                        <div className="text-xs text-blue-600">
                          {Math.round(route.preference_score * 100)}% of your travel
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">
                  Book more flights to see your favorite routes!
                </p>
              )}
            </div>
          </Card>
        </div>

        {/* Seasonal Preferences */}
        {Object.keys(preferences.seasonal_preferences).length > 0 && (
          <Card className="mb-8">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                🌍 Seasonal Travel Patterns
              </h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(preferences.seasonal_preferences).map(([season, count]) => (
                  <div key={season} className="text-center p-4 bg-gray-50 rounded">
                    <div className="text-2xl mb-2">
                      {season === 'spring' ? '🌸' : 
                       season === 'summer' ? '☀️' : 
                       season === 'autumn' ? '🍂' : '❄️'}
                    </div>
                    <div className="font-medium text-gray-900 capitalize">{season}</div>
                    <div className="text-sm text-gray-600">{count} trips</div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Recommended Flights */}
        {recommended_flights.length > 0 && (
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                🤖 Flights You Might Like
              </h3>
              
              <div className="space-y-4">
                {recommended_flights.map((flight, index) => (
                  <div key={flight.id} className="border-l-4 border-blue-500 pl-4 py-3 bg-gray-50 rounded-r">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {flight.from_city} → {flight.to_city}
                        </h4>
                        <p className="text-sm text-gray-600">
                          {new Date(flight.departure_time).toLocaleDateString()} • {flight.airline}
                        </p>
                        <p className="text-sm text-blue-600 font-medium">
                          ₹{flight.price.toLocaleString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-green-600">
                          {Math.round(flight.score)}% match
                        </div>
                      </div>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {flight.reasons.map((reason, idx) => (
                        <span
                          key={idx}
                          className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                        >
                          {reason}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Analysis Summary */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Analysis based on {data_points} data points from your booking history
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Your preferences are updated automatically as you book more flights
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default UserInsights;