import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function SmartRecommendations({ 
  type = 'flight', 
  flightId = null,
  currency = 'USD',
  region = 'US',
  onRecommendationSelect 
}) {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [userInsights, setUserInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [smartSearchResults, setSmartSearchResults] = useState([]);
  const [trendingDestinations, setTrendingDestinations] = useState([]);

  useEffect(() => {
    if (user) {
      fetchRecommendations();
      fetchUserInsights();
      fetchTrendingDestinations();
    }
  }, [user, type, flightId, currency, region]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      let response;
      
      if (type === 'flight') {
        response = await api.get('/smart-recommendations/flight-recommendations', {
          params: { currency, region, limit: 8 }
        });
      } else if (type === 'seat' && flightId) {
        response = await api.get(`/smart-recommendations/seat-recommendations/${flightId}`);
      }
      
      if (response) {
        setRecommendations(response.data.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserInsights = async () => {
    try {
      const response = await api.get('/smart-recommendations/user-insights');
      setUserInsights(response.data);
    } catch (error) {
      console.error('Failed to fetch user insights:', error);
    }
  };

  const fetchTrendingDestinations = async () => {
    try {
      const response = await api.get('/smart-recommendations/trending-destinations', {
        params: { currency, region, limit: 5 }
      });
      setTrendingDestinations(response.data.trending_destinations || []);
    } catch (error) {
      console.error('Failed to fetch trending destinations:', error);
    }
  };

  const handleSmartSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      const response = await api.post('/smart-recommendations/smart-search', {
        query: searchQuery,
        currency,
        region
      });
      
      setSmartSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Smart search failed:', error);
    }
  };

  const handleRecommendationClick = (recommendation) => {
    if (onRecommendationSelect) {
      onRecommendationSelect(recommendation);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Smart Search */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-xl border border-purple-200">
        <h3 className="text-lg font-bold text-purple-800 mb-4">
          🤖 AI-Powered Smart Search
        </h3>
        <div className="flex gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Try: 'cheap flight to Mumbai tomorrow' or 'window seat business class'"
            className="flex-1 px-4 py-2 border border-purple-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            onKeyPress={(e) => e.key === 'Enter' && handleSmartSearch()}
          />
          <button
            onClick={handleSmartSearch}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            🔍 Search
          </button>
        </div>
        
        {/* Smart Search Results */}
        {smartSearchResults.length > 0 && (
          <div className="mt-4 space-y-3">
            <h4 className="font-semibold text-purple-700">Smart Search Results:</h4>
            {smartSearchResults.slice(0, 3).map((result, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white p-4 rounded-lg border border-purple-200 cursor-pointer hover:border-purple-400 transition-colors"
                onClick={() => handleRecommendationClick(result)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h5 className="font-semibold text-gray-800">{result.title}</h5>
                    <p className="text-sm text-gray-600 mt-1">{result.description}</p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {result.reasons.slice(0, 2).map((reason, i) => (
                        <span key={i} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                          {reason}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-purple-600">
                      {result.price_info?.formatted_price || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-500">
                      Score: {result.score.toFixed(1)}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* User Insights Panel */}
      {userInsights && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
          <h3 className="text-lg font-bold text-blue-800 mb-4">
            📊 Your Travel Insights
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg">
              <h4 className="font-semibold text-blue-700 mb-2">Booking Pattern</h4>
              <p className="text-sm text-gray-600">
                You typically book {userInsights.booking_insights?.typical_advance_booking} in advance
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Price sensitivity: {userInsights.booking_insights?.price_sensitivity}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <h4 className="font-semibold text-blue-700 mb-2">Preferences</h4>
              <p className="text-sm text-gray-600">
                Seat: {userInsights.booking_insights?.seat_preferences?.class} class, {userInsights.booking_insights?.seat_preferences?.position}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Times: {userInsights.booking_insights?.preferred_times?.join(', ') || 'Any time'}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <h4 className="font-semibold text-blue-700 mb-2">Recommendations</h4>
              <p className="text-sm text-gray-600">
                Best booking time: {userInsights.recommendations?.best_booking_time}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Trending Destinations */}
      {trendingDestinations.length > 0 && type === 'flight' && (
        <div className="bg-gradient-to-r from-orange-50 to-red-50 p-6 rounded-xl border border-orange-200">
          <h3 className="text-lg font-bold text-orange-800 mb-4">
            🔥 Trending Destinations
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {trendingDestinations.map((destination, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white p-4 rounded-lg border border-orange-200 hover:border-orange-400 transition-colors cursor-pointer"
                onClick={() => handleRecommendationClick({
                  type: 'trending_destination',
                  destination: destination.destination,
                  metadata: destination
                })}
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-gray-800">{destination.destination}</h4>
                  <div className="text-sm bg-orange-100 text-orange-700 px-2 py-1 rounded">
                    {destination.trend_score}% 📈
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-2">
                  From: {destination.from_cities.slice(0, 2).join(', ')}
                  {destination.from_cities.length > 2 && ` +${destination.from_cities.length - 2} more`}
                </p>
                <div className="flex justify-between items-center">
                  <div className="text-lg font-bold text-orange-600">
                    {destination.price_info?.formatted_price}
                  </div>
                  <div className="text-xs text-gray-500">
                    {destination.seasonal_factor}
                  </div>
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {destination.reasons.slice(0, 2).map((reason, i) => (
                    <span key={i} className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded">
                      {reason}
                    </span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Main Recommendations */}
      <div>
        <h3 className="text-lg font-bold text-gray-800 mb-4">
          {type === 'flight' ? '✈️ Personalized Flight Recommendations' : '💺 Smart Seat Recommendations'}
        </h3>
        
        {recommendations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-4">🤖</div>
            <p>No personalized recommendations available yet.</p>
            <p className="text-sm mt-2">Book a few flights to help our AI learn your preferences!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <AnimatePresence>
              {recommendations.map((rec, index) => (
                <motion.div
                  key={rec.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white p-6 rounded-xl border border-gray-200 hover:border-blue-400 hover:shadow-lg transition-all cursor-pointer"
                  onClick={() => handleRecommendationClick(rec)}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-800 text-lg">{rec.title}</h4>
                      <p className="text-gray-600 text-sm mt-1">{rec.description}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-blue-600">
                        {rec.price_info?.formatted_price || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-500">
                        AI Score: {rec.score.toFixed(1)}
                      </div>
                    </div>
                  </div>
                  
                  {/* Recommendation Reasons */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {rec.reasons.slice(0, 3).map((reason, i) => (
                      <span 
                        key={i} 
                        className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full"
                      >
                        {reason}
                      </span>
                    ))}
                  </div>
                  
                  {/* Additional Info */}
                  {rec.metadata && (
                    <div className="text-xs text-gray-500 space-y-1">
                      {rec.metadata.departure_time && (
                        <div>🕒 {new Date(rec.metadata.departure_time).toLocaleString()}</div>
                      )}
                      {rec.metadata.airline && (
                        <div>✈️ {rec.metadata.airline}</div>
                      )}
                      {rec.metadata.seat_class && (
                        <div>💺 {rec.metadata.seat_class} - Row {rec.metadata.row}, Col {rec.metadata.col}</div>
                      )}
                    </div>
                  )}
                  
                  {/* Price Conversion Info */}
                  {rec.price_info?.regional_adjustment && rec.price_info.regional_adjustment !== 1.0 && (
                    <div className="mt-3 p-2 bg-green-50 rounded text-xs text-green-700">
                      💰 Regional pricing applied ({(rec.price_info.regional_adjustment * 100).toFixed(0)}% of US price)
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}