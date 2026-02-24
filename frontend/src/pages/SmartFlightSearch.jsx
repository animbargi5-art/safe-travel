import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CurrencySelector from '../components/CurrencySelector';
import SmartRecommendations from '../components/SmartRecommendations';
import api from '../services/api';

export default function SmartFlightSearch() {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // Search state
  const [searchParams, setSearchParams] = useState({
    from_city: '',
    to_city: '',
    departure_date: '',
    return_date: '',
    passengers: 1,
    class: 'ECONOMY'
  });
  
  // Multi-currency state
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [selectedRegion, setSelectedRegion] = useState('US');
  const [exchangeRates, setExchangeRates] = useState({});
  
  // Results state
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [priceComparison, setPriceComparison] = useState({});
  
  // Smart features state
  const [showRecommendations, setShowRecommendations] = useState(true);
  const [priceAlerts, setPriceAlerts] = useState([]);
  const [currencyTrends, setCurrencyTrends] = useState({});

  const regions = [
    { code: 'US', name: 'United States', flag: '🇺🇸' },
    { code: 'EU', name: 'Europe', flag: '🇪🇺' },
    { code: 'ASIA', name: 'Asia', flag: '🌏' },
    { code: 'MIDDLE_EAST', name: 'Middle East', flag: '🕌' },
    { code: 'OCEANIA', name: 'Oceania', flag: '🇦🇺' },
    { code: 'AFRICA', name: 'Africa', flag: '🌍' },
    { code: 'SOUTH_AMERICA', name: 'South America', flag: '🌎' }
  ];

  useEffect(() => {
    if (selectedCurrency !== 'USD') {
      fetchCurrencyTrends();
    }
  }, [selectedCurrency]);

  const fetchCurrencyTrends = async () => {
    try {
      const response = await api.get(`/currency/trends/${selectedCurrency}`);
      setCurrencyTrends(response.data);
    } catch (error) {
      console.error('Failed to fetch currency trends:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchParams.from_city || !searchParams.to_city) {
      alert('Please enter both departure and destination cities');
      return;
    }

    setLoading(true);
    try {
      // Search flights
      const response = await api.get('/flights/search', {
        params: {
          from_city: searchParams.from_city,
          to_city: searchParams.to_city,
          departure_date: searchParams.departure_date || undefined
        }
      });

      let flightResults = response.data.flights || [];

      // Convert prices to selected currency
      if (selectedCurrency !== 'USD') {
        const convertedFlights = await Promise.all(
          flightResults.map(async (flight) => {
            try {
              const conversionResponse = await api.post('/currency/convert', {
                amount: flight.price,
                from_currency: 'USD',
                to_currency: selectedCurrency
              });

              // Get regional pricing
              const regionalResponse = await api.post('/currency/regional-price', {
                base_price_usd: flight.price,
                region: selectedRegion,
                target_currency: selectedCurrency
              });

              return {
                ...flight,
                original_price_usd: flight.price,
                converted_price: conversionResponse.data.converted_amount,
                regional_price: regionalResponse.data.converted_amount,
                currency: selectedCurrency,
                formatted_price: regionalResponse.data.formatted_amount,
                regional_multiplier: regionalResponse.data.regional_multiplier,
                exchange_rate: conversionResponse.data.exchange_rate
              };
            } catch (error) {
              console.error('Price conversion failed for flight:', flight.id);
              return flight;
            }
          })
        );
        flightResults = convertedFlights;
      }

      setFlights(flightResults);
      
      // Generate price comparison
      if (flightResults.length > 0) {
        generatePriceComparison(flightResults);
      }

    } catch (error) {
      console.error('Flight search failed:', error);
      alert('Flight search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const generatePriceComparison = async (flights) => {
    try {
      const avgPrice = flights.reduce((sum, flight) => sum + (flight.converted_price || flight.price), 0) / flights.length;
      
      // Compare with other currencies
      const comparisons = {};
      const currencies = ['USD', 'EUR', 'GBP', 'INR'];
      
      for (const currency of currencies) {
        if (currency !== selectedCurrency) {
          const response = await api.post('/currency/convert', {
            amount: avgPrice,
            from_currency: selectedCurrency,
            to_currency: currency
          });
          comparisons[currency] = response.data;
        }
      }
      
      setPriceComparison({
        average_price: avgPrice,
        currency: selectedCurrency,
        comparisons
      });
    } catch (error) {
      console.error('Price comparison failed:', error);
    }
  };

  const handleFlightSelect = (flight) => {
    // Store flight selection and navigate to seat selection
    localStorage.setItem('selectedFlight', JSON.stringify({
      ...flight,
      search_params: searchParams,
      currency: selectedCurrency,
      region: selectedRegion
    }));
    
    navigate(`/seats/${flight.id}`);
  };

  const handleRecommendationSelect = (recommendation) => {
    if (recommendation.metadata?.flight_id) {
      const flight = flights.find(f => f.id === recommendation.metadata.flight_id);
      if (flight) {
        handleFlightSelect(flight);
      }
    } else if (recommendation.type === 'trending_destination') {
      setSearchParams(prev => ({
        ...prev,
        to_city: recommendation.destination
      }));
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          🌍 Smart Flight Search with Multi-Currency Support
        </h1>
        <p className="text-gray-600">
          AI-powered recommendations with real-time currency conversion and regional pricing
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* From City */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">From</label>
            <input
              type="text"
              value={searchParams.from_city}
              onChange={(e) => setSearchParams(prev => ({ ...prev, from_city: e.target.value }))}
              placeholder="Departure city"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* To City */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">To</label>
            <input
              type="text"
              value={searchParams.to_city}
              onChange={(e) => setSearchParams(prev => ({ ...prev, to_city: e.target.value }))}
              placeholder="Destination city"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Departure Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Departure</label>
            <input
              type="date"
              value={searchParams.departure_date}
              onChange={(e) => setSearchParams(prev => ({ ...prev, departure_date: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Class */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Class</label>
            <select
              value={searchParams.class}
              onChange={(e) => setSearchParams(prev => ({ ...prev, class: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ECONOMY">Economy</option>
              <option value="BUSINESS">Business</option>
              <option value="FIRST">First Class</option>
            </select>
          </div>
        </div>

        {/* Currency and Region Selection */}
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
            <CurrencySelector
              selectedCurrency={selectedCurrency}
              onCurrencyChange={setSelectedCurrency}
              region={selectedRegion}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Region</label>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {regions.map(region => (
                <option key={region.code} value={region.code}>
                  {region.flag} {region.name}
                </option>
              ))}
            </select>
          </div>

          {/* Currency Trend Indicator */}
          {currencyTrends.trend_direction && (
            <div className="bg-blue-50 px-3 py-2 rounded-lg">
              <div className="text-sm font-medium text-blue-800">
                {selectedCurrency} Trend
              </div>
              <div className={`text-sm ${
                currencyTrends.trend_direction === 'up' ? 'text-green-600' : 
                currencyTrends.trend_direction === 'down' ? 'text-red-600' : 'text-gray-600'
              }`}>
                {currencyTrends.trend_direction === 'up' ? '📈' : 
                 currencyTrends.trend_direction === 'down' ? '📉' : '➡️'} 
                {currencyTrends.overall_change_percent?.toFixed(2)}%
              </div>
            </div>
          )}
        </div>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors font-medium"
        >
          {loading ? '🔍 Searching...' : '🚀 Search Flights'}
        </button>
      </div>

      {/* Smart Recommendations */}
      {showRecommendations && (
        <div className="mb-8">
          <SmartRecommendations
            type="flight"
            currency={selectedCurrency}
            region={selectedRegion}
            onRecommendationSelect={handleRecommendationSelect}
          />
        </div>
      )}

      {/* Price Comparison */}
      {Object.keys(priceComparison).length > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-xl border border-green-200 mb-8">
          <h3 className="text-lg font-bold text-green-800 mb-4">💰 Price Comparison</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-600">Average in {selectedCurrency}</div>
              <div className="text-xl font-bold text-green-600">
                {priceComparison.average_price?.toFixed(2)}
              </div>
            </div>
            {Object.entries(priceComparison.comparisons || {}).map(([currency, data]) => (
              <div key={currency} className="text-center">
                <div className="text-sm text-gray-600">In {currency}</div>
                <div className="text-lg font-semibold text-gray-800">
                  {data.formatted_amount}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Flight Results */}
      {flights.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-800 mb-6">
            ✈️ Flight Results ({flights.length} flights found)
          </h3>
          <div className="space-y-4">
            <AnimatePresence>
              {flights.map((flight, index) => (
                <motion.div
                  key={flight.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white p-6 rounded-xl border border-gray-200 hover:border-blue-400 hover:shadow-lg transition-all cursor-pointer"
                  onClick={() => handleFlightSelect(flight)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <h4 className="text-xl font-bold text-gray-800">
                          {flight.from_city} → {flight.to_city}
                        </h4>
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          {flight.airline}
                        </span>
                      </div>
                      
                      <div className="text-gray-600 space-y-1">
                        <div>🕒 Departure: {new Date(flight.departure_time).toLocaleString()}</div>
                        <div>🛬 Arrival: {new Date(flight.arrival_time).toLocaleString()}</div>
                        <div>⏱️ Duration: {flight.duration}</div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600 mb-1">
                        {flight.formatted_price || `${selectedCurrency} ${flight.converted_price?.toFixed(2) || flight.price}`}
                      </div>
                      
                      {flight.regional_multiplier && flight.regional_multiplier !== 1.0 && (
                        <div className="text-sm text-green-600 mb-1">
                          💰 Regional pricing ({(flight.regional_multiplier * 100).toFixed(0)}% of US price)
                        </div>
                      )}
                      
                      {flight.original_price_usd && selectedCurrency !== 'USD' && (
                        <div className="text-sm text-gray-500">
                          Original: ${flight.original_price_usd}
                        </div>
                      )}
                      
                      {flight.exchange_rate && (
                        <div className="text-xs text-gray-400">
                          Rate: 1 USD = {flight.exchange_rate.toFixed(4)} {selectedCurrency}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="flex justify-between items-center">
                      <div className="text-sm text-gray-500">
                        Flight {flight.flight_number} • {flight.aircraft_type}
                      </div>
                      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                        Select Flight →
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* No Results */}
      {!loading && flights.length === 0 && searchParams.from_city && searchParams.to_city && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">✈️</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No flights found</h3>
          <p className="text-gray-500 mb-4">
            Try different cities or dates. Our AI recommendations above might help!
          </p>
          <button
            onClick={() => setShowRecommendations(true)}
            className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
          >
            🤖 Show AI Recommendations
          </button>
        </div>
      )}
    </div>
  );
}