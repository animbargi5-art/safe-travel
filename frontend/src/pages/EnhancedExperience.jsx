import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import VoiceBooking from '../components/VoiceBooking';
import SocialBooking from '../components/SocialBooking';
import LoyaltyProgram from '../components/LoyaltyProgram';
import SmartRecommendations from '../components/SmartRecommendations';
import api from '../services/api';

export default function EnhancedExperience() {
  const { user } = useAuth();
  const [activeFeature, setActiveFeature] = useState('voice');
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const features = [
    {
      id: 'voice',
      title: 'Voice Booking',
      icon: '🎤',
      description: 'Book flights using natural voice commands',
      color: 'from-purple-500 to-blue-500'
    },
    {
      id: 'social',
      title: 'Social Booking',
      icon: '👥',
      description: 'Invite friends and family to join your flights',
      color: 'from-pink-500 to-purple-500'
    },
    {
      id: 'loyalty',
      title: 'Loyalty Program',
      icon: '🏆',
      description: 'Earn points and unlock exclusive benefits',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      id: 'smart',
      title: 'Smart Recommendations',
      icon: '🤖',
      description: 'AI-powered personalized flight suggestions',
      color: 'from-green-500 to-teal-500'
    }
  ];

  const handleVoiceSearchResult = async (parameters) => {
    if (!parameters.from_city || !parameters.to_city) return;

    setIsSearching(true);
    try {
      const response = await api.get('/flights/search', {
        params: {
          from_city: parameters.from_city,
          to_city: parameters.to_city,
          departure_date: parameters.departure_date
        }
      });

      setSearchResults(response.data.flights || []);
      setActiveFeature('results');
    } catch (error) {
      console.error('Flight search failed:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleFlightSelect = (flight) => {
    setSelectedFlight(flight);
    setActiveFeature('social');
  };

  const handleRecommendationSelect = (recommendation) => {
    if (recommendation.metadata?.flight_id) {
      // Find flight in search results or fetch it
      const flight = searchResults.find(f => f.id === recommendation.metadata.flight_id);
      if (flight) {
        handleFlightSelect(flight);
      }
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center p-8 bg-white rounded-xl shadow-lg">
          <div className="text-6xl mb-4">✈️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Enhanced Flight Experience</h2>
          <p className="text-gray-600 mb-6">
            Please log in to access voice booking, social features, and loyalty rewards
          </p>
          <button
            onClick={() => window.location.href = '/login'}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Sign In to Continue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              🚀 Enhanced Flight Experience
            </h1>
            <p className="text-gray-600">
              Next-generation features for modern travelers
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Feature Navigation */}
        <div className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {features.map((feature) => (
              <motion.button
                key={feature.id}
                onClick={() => setActiveFeature(feature.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`p-6 rounded-xl text-white font-semibold transition-all ${
                  activeFeature === feature.id
                    ? `bg-gradient-to-r ${feature.color} shadow-lg`
                    : 'bg-gray-400 hover:bg-gray-500'
                }`}
              >
                <div className="text-3xl mb-2">{feature.icon}</div>
                <div className="text-lg mb-1">{feature.title}</div>
                <div className="text-sm opacity-90">{feature.description}</div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Feature Content */}
        <AnimatePresence mode="wait">
          {activeFeature === 'voice' && (
            <motion.div
              key="voice"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            >
              <VoiceBooking onSearchResult={handleVoiceSearchResult} />
              
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">🎯 Voice Features</h3>
                
                <div className="space-y-4">
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">🗣️</div>
                    <div>
                      <h4 className="font-semibold text-gray-800">Natural Language</h4>
                      <p className="text-gray-600 text-sm">
                        Speak naturally: "Find cheap flights to Mumbai tomorrow morning"
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">🌍</div>
                    <div>
                      <h4 className="font-semibold text-gray-800">Global Cities</h4>
                      <p className="text-gray-600 text-sm">
                        Supports 100+ cities worldwide with smart recognition
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">⚡</div>
                    <div>
                      <h4 className="font-semibold text-gray-800">Instant Processing</h4>
                      <p className="text-gray-600 text-sm">
                        AI processes your request in milliseconds
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">🎯</div>
                    <div>
                      <h4 className="font-semibold text-gray-800">Smart Context</h4>
                      <p className="text-gray-600 text-sm">
                        Understands preferences, dates, and booking intent
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h5 className="font-semibold text-blue-800 mb-2">💡 Pro Tips</h5>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Include departure and destination cities</li>
                    <li>• Mention specific dates or time preferences</li>
                    <li>• Specify number of passengers if more than one</li>
                    <li>• Use class preferences: economy, business, first</li>
                  </ul>
                </div>
              </div>
            </motion.div>
          )}

          {activeFeature === 'social' && (
            <motion.div
              key="social"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            >
              <SocialBooking flight={selectedFlight} />
              
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">👥 Social Benefits</h3>
                
                <div className="space-y-4">
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">🎯</div>
                    <div>
                      <h4 className="font-semibold text-gray-800">Guaranteed Seats Together</h4>
                      <p className="text-gray-600 text-sm">
                        Book as a group to ensure everyone sits together
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">💰</div>
                    <div>
                      <h4 className="font-semibold text-gray-800">Group Discounts</h4>
                      <p className="text-gray-600 text-sm">
                        Potential savings for larger groups (5+ people)
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">📱</div>
                    <div>
                      <h4 className="font-semibold text-gray-800">Real-time Updates</h4>
                      <p className="text-gray-600 text-sm">
                        Everyone gets instant notifications about booking status
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">✉️</div>
                    <div>
                      <h4 className="font-semibold text-gray-800">Easy Invitations</h4>
                      <p className="text-gray-600 text-sm">
                        Send beautiful email invitations with one click
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-pink-50 rounded-lg">
                  <h5 className="font-semibold text-pink-800 mb-2">🎉 Perfect For</h5>
                  <ul className="text-sm text-pink-700 space-y-1">
                    <li>• Family vacations and reunions</li>
                    <li>• Friends' getaways and adventures</li>
                    <li>• Business team travel</li>
                    <li>• Wedding parties and celebrations</li>
                    <li>• Group tours and excursions</li>
                  </ul>
                </div>

                {!selectedFlight && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      💡 Use voice booking or search to select a flight first, then invite your group!
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeFeature === 'loyalty' && (
            <motion.div
              key="loyalty"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <LoyaltyProgram />
            </motion.div>
          )}

          {activeFeature === 'smart' && (
            <motion.div
              key="smart"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <SmartRecommendations
                type="flight"
                currency="USD"
                region="US"
                onRecommendationSelect={handleRecommendationSelect}
              />
            </motion.div>
          )}

          {activeFeature === 'results' && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  ✈️ Voice Search Results
                </h3>
                
                {isSearching ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Searching flights...</p>
                  </div>
                ) : searchResults.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <div className="text-4xl mb-4">🔍</div>
                    <p>No flights found for your voice search.</p>
                    <p className="text-sm mt-2">Try using voice booking again with different criteria.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {searchResults.map((flight, index) => (
                      <motion.div
                        key={flight.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer"
                        onClick={() => handleFlightSelect(flight)}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-4 mb-2">
                              <h4 className="text-lg font-semibold text-gray-800">
                                {flight.from_city} → {flight.to_city}
                              </h4>
                              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                                {flight.airline}
                              </span>
                            </div>
                            
                            <div className="text-gray-600 text-sm space-y-1">
                              <div>🕒 Departure: {new Date(flight.departure_time).toLocaleString()}</div>
                              <div>🛬 Arrival: {new Date(flight.arrival_time).toLocaleString()}</div>
                              <div>⏱️ Duration: {flight.duration}</div>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <div className="text-2xl font-bold text-blue-600 mb-1">
                              ${flight.price}
                            </div>
                            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                              Select Flight
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Feature Highlights */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-lg text-center">
            <div className="text-3xl mb-3">🎤</div>
            <h4 className="font-semibold text-gray-800 mb-2">Voice Commands</h4>
            <p className="text-gray-600 text-sm">
              87% accuracy with natural language processing
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-lg text-center">
            <div className="text-3xl mb-3">👥</div>
            <h4 className="font-semibold text-gray-800 mb-2">Group Bookings</h4>
            <p className="text-gray-600 text-sm">
              Up to 10 people per social booking invitation
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-lg text-center">
            <div className="text-3xl mb-3">🏆</div>
            <h4 className="font-semibold text-gray-800 mb-2">Loyalty Tiers</h4>
            <p className="text-gray-600 text-sm">
              5 tiers with up to 20% discounts and 2x points
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-lg text-center">
            <div className="text-3xl mb-3">🤖</div>
            <h4 className="font-semibold text-gray-800 mb-2">AI Recommendations</h4>
            <p className="text-gray-600 text-sm">
              Personalized suggestions based on your history
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}