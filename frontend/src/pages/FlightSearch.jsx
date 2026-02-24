import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import SectionTitle from "../components/ui/SectionTitle";
import PageWrapper from "../components/PageWrapper";
import MLRecommendations from "../components/MLRecommendations";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function FlightSearch() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const [fromCity, setFromCity] = useState("");
  const [toCity, setToCity] = useState("");
  const [departureDate, setDepartureDate] = useState("");
  const [returnDate, setReturnDate] = useState("");
  const [isRoundTrip, setIsRoundTrip] = useState(false);
  const [loading, setLoading] = useState(false);
  const [cities, setCities] = useState([]);
  const [popularRoutes, setPopularRoutes] = useState([]);
  const [priceRange, setPriceRange] = useState({ min: 0, max: 100000 });

  // Load cities and popular routes on component mount
  useEffect(() => {
    loadCities();
    loadPopularRoutes();
    loadPriceRange();
  }, []);

  const loadCities = async () => {
    try {
      const response = await api.get('/flights/cities');
      setCities(response.data.cities || []);
    } catch (error) {
      console.error('Failed to load cities:', error);
    }
  };

  const loadPopularRoutes = async () => {
    try {
      const response = await api.get('/flights/popular-routes');
      setPopularRoutes(response.data || []);
    } catch (error) {
      console.error('Failed to load popular routes:', error);
    }
  };

  const loadPriceRange = async () => {
    try {
      const response = await api.get('/flights/price-range');
      setPriceRange({
        min: response.data.min_price || 0,
        max: response.data.max_price || 100000
      });
    } catch (error) {
      console.error('Failed to load price range:', error);
    }
  };

  const handleSearch = () => {
    if (!fromCity || !toCity) {
      alert('Please select both departure and destination cities');
      return;
    }

    setLoading(true);
    
    // Build search parameters
    const searchParams = new URLSearchParams({
      from_city: fromCity,
      to_city: toCity,
    });

    if (departureDate) {
      searchParams.append('departure_date', departureDate);
    }

    // Navigate to flights page with search parameters
    navigate(`/flights?${searchParams.toString()}`);
  };

  const handlePopularRouteClick = (route) => {
    setFromCity(route.from_city);
    setToCity(route.to_city);
  };

  const swapCities = () => {
    const temp = fromCity;
    setFromCity(toCity);
    setToCity(temp);
  };

  // Get today's date for min date input
  const today = new Date().toISOString().split('T')[0];

  return (
    <PageWrapper>
      <SectionTitle
        title="Search Flights"
        subtitle="Find your perfect journey with mindful intention"
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.4 }}
        className="max-w-4xl mx-auto"
      >
        {/* Main Search Form */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          {/* Trip Type Toggle */}
          <div className="flex justify-center mb-6">
            <div className="bg-gray-100 rounded-lg p-1 flex">
              <button
                onClick={() => setIsRoundTrip(false)}
                className={`px-6 py-2 rounded-md transition ${
                  !isRoundTrip 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                One Way
              </button>
              <button
                onClick={() => setIsRoundTrip(true)}
                className={`px-6 py-2 rounded-md transition ${
                  isRoundTrip 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                Round Trip
              </button>
            </div>
          </div>

          {/* Search Form */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {/* From City */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                From
              </label>
              <select
                value={fromCity}
                onChange={(e) => setFromCity(e.target.value)}
                className="w-full border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white"
              >
                <option value="">Select departure city</option>
                {cities.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>

            {/* To City */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                To
              </label>
              <div className="flex">
                <select
                  value={toCity}
                  onChange={(e) => setToCity(e.target.value)}
                  className="flex-1 border border-gray-300 rounded-l-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white"
                >
                  <option value="">Select destination</option>
                  {cities.filter(city => city !== fromCity).map(city => (
                    <option key={city} value={city}>{city}</option>
                  ))}
                </select>
                <button
                  onClick={swapCities}
                  className="px-3 border border-l-0 border-gray-300 rounded-r-xl hover:bg-gray-50 transition"
                  title="Swap cities"
                >
                  ⇄
                </button>
              </div>
            </div>

            {/* Departure Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Departure
              </label>
              <input
                type="date"
                value={departureDate}
                onChange={(e) => setDepartureDate(e.target.value)}
                min={today}
                className="w-full border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
            </div>

            {/* Return Date (if round trip) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {isRoundTrip ? 'Return' : 'Passengers'}
              </label>
              {isRoundTrip ? (
                <input
                  type="date"
                  value={returnDate}
                  onChange={(e) => setReturnDate(e.target.value)}
                  min={departureDate || today}
                  className="w-full border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              ) : (
                <select className="w-full border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                  <option>1 Passenger</option>
                  <option>2 Passengers</option>
                  <option>3 Passengers</option>
                  <option>4+ Passengers</option>
                </select>
              )}
            </div>
          </div>

          {/* Search Button */}
          <div className="text-center">
            <button
              onClick={handleSearch}
              disabled={loading || !fromCity || !toCity}
              className="px-8 py-3 bg-blue-600 text-white rounded-xl text-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Search Flights ✈️'}
            </button>
          </div>
        </div>

        {/* ML Recommendations for logged-in users */}
        {user && <MLRecommendations type="flights" limit={3} />}

        {/* Popular Routes */}
        {popularRoutes.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              🔥 Popular Routes
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {popularRoutes.slice(0, 6).map((route, index) => (
                <button
                  key={index}
                  onClick={() => handlePopularRouteClick(route)}
                  className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition text-left"
                >
                  <div className="font-medium text-gray-800">
                    {route.from_city} → {route.to_city}
                  </div>
                  <div className="text-sm text-gray-500">
                    From ₹{route.min_price.toLocaleString()}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Price Range Info */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              💰 Current Price Range
            </h3>
            <div className="flex justify-center items-center space-x-4 text-sm text-gray-600">
              <span>Budget: ₹{priceRange.min.toLocaleString()}</span>
              <span>•</span>
              <span>Premium: ₹{priceRange.max.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Dharma Message */}
        <div className="text-center mt-8">
          <p className="text-gray-400 text-sm italic">
            "Every journey begins with a clear intention. Choose your path with mindfulness."
          </p>
        </div>
      </motion.div>
    </PageWrapper>
  );
}
