import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate, useSearchParams } from "react-router-dom";
import PageWrapper from "../components/PageWrapper";
import api from "../services/api";
import SectionTitle from "../components/ui/SectionTitle";
import LoadingState from "../components/ui/LoadingState";
import EmptyState from "../components/ui/EmptyState";

export default function Flights() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    from_city: searchParams.get('from_city') || '',
    to_city: searchParams.get('to_city') || '',
    departure_date: searchParams.get('departure_date') || '',
    min_price: '',
    max_price: '',
    sort_by: 'price',
    sort_order: 'asc'
  });

  // Search flights based on current filters
  const searchFlights = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {};
      
      // Only add non-empty parameters
      Object.keys(filters).forEach(key => {
        if (filters[key] && filters[key] !== '') {
          params[key] = filters[key];
        }
      });

      const response = await api.get("/flights/search", { params });
      setFlights(response.data || []);
      
      if (response.data.length === 0) {
        setError("No flights found for your search criteria. Try adjusting your filters.");
      }
    } catch (err) {
      console.error('Search error:', err);
      setError("Failed to search flights. Please try again.");
      setFlights([]);
    } finally {
      setLoading(false);
    }
  };

  // Search on component mount and when filters change
  useEffect(() => {
    searchFlights();
  }, []);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSearch = () => {
    searchFlights();
  };

  const clearFilters = () => {
    setFilters({
      from_city: '',
      to_city: '',
      departure_date: '',
      min_price: '',
      max_price: '',
      sort_by: 'price',
      sort_order: 'asc'
    });
  };

  const formatDuration = (minutes) => {
    if (!minutes) return 'N/A';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return 'N/A';
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
        title="Available Flights"
        subtitle="Choose a journey that suits your path"
      />
      
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="min-h-[70vh]"
      >
        {/* Enhanced Search & Filter Bar */}
        <div className="bg-white rounded-2xl shadow-sm hover:shadow-md transition p-6 max-w-6xl mx-auto mb-8">
          {/* Search Inputs */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <input
              value={filters.from_city}
              onChange={(e) => handleFilterChange('from_city', e.target.value)}
              placeholder="From City"
              className="border rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <input
              value={filters.to_city}
              onChange={(e) => handleFilterChange('to_city', e.target.value)}
              placeholder="To City"
              className="border rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <input
              type="date"
              value={filters.departure_date}
              onChange={(e) => handleFilterChange('departure_date', e.target.value)}
              className="border rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <button
              onClick={handleSearch}
              className="bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition font-semibold"
            >
              Search Flights
            </button>
          </div>

          {/* Advanced Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
            <input
              type="number"
              value={filters.min_price}
              onChange={(e) => handleFilterChange('min_price', e.target.value)}
              placeholder="Min Price (₹)"
              className="border rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <input
              type="number"
              value={filters.max_price}
              onChange={(e) => handleFilterChange('max_price', e.target.value)}
              placeholder="Max Price (₹)"
              className="border rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <select
              value={filters.sort_by}
              onChange={(e) => handleFilterChange('sort_by', e.target.value)}
              className="border rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white"
            >
              <option value="price">Sort by Price</option>
              <option value="departure_time">Sort by Departure</option>
              <option value="duration">Sort by Duration</option>
            </select>
            <div className="flex space-x-2">
              <select
                value={filters.sort_order}
                onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                className="flex-1 border rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white"
              >
                <option value="asc">Low to High</option>
                <option value="desc">High to Low</option>
              </select>
              <button
                onClick={clearFilters}
                className="px-4 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition text-sm"
              >
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Results Summary */}
        {!loading && flights.length > 0 && (
          <div className="max-w-6xl mx-auto mb-6">
            <p className="text-gray-600">
              Found {flights.length} flight{flights.length !== 1 ? 's' : ''} 
              {filters.from_city && filters.to_city && 
                ` from ${filters.from_city} to ${filters.to_city}`
              }
            </p>
          </div>
        )}

        {/* Loading State */}
        {loading && <LoadingState message="Searching for flights..." />}

        {/* Error State */}
        {error && !loading && (
          <EmptyState 
            title="No flights found"
            message={error}
            actionText="Modify Search"
            onAction={() => navigate('/search')}
          />
        )}

        {/* Flights List */}
        <div className="max-w-6xl mx-auto grid gap-6">
          {flights.map((flight) => (
            <motion.div
              key={flight.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-2xl shadow-sm hover:shadow-md transition p-6"
            >
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                {/* Flight Info */}
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-4">
                      <h3 className="text-xl font-semibold text-gray-800">
                        {flight.from_city} → {flight.to_city}
                      </h3>
                      {flight.airline && (
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                          {flight.airline}
                        </span>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        ₹{flight.price.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-500">per person</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                    <div>
                      <div className="font-medium text-gray-800">Departure</div>
                      <div>{formatDateTime(flight.departure_time)}</div>
                      {flight.from_airport_code && (
                        <div className="text-xs text-gray-500">{flight.from_airport_code}</div>
                      )}
                    </div>
                    
                    <div>
                      <div className="font-medium text-gray-800">Arrival</div>
                      <div>{formatDateTime(flight.arrival_time)}</div>
                      {flight.to_airport_code && (
                        <div className="text-xs text-gray-500">{flight.to_airport_code}</div>
                      )}
                    </div>
                    
                    <div>
                      <div className="font-medium text-gray-800">Duration</div>
                      <div>{formatDuration(flight.duration)}</div>
                      {flight.aircraft_type && (
                        <div className="text-xs text-gray-500">{flight.aircraft_type}</div>
                      )}
                    </div>
                  </div>

                  {flight.flight_number && (
                    <div className="mt-2 text-xs text-gray-500">
                      Flight {flight.flight_number}
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="mt-4 lg:mt-0 lg:ml-6 flex flex-col space-y-2">
                  <button
                    onClick={() => navigate(`/seats/${flight.id}`)}
                    className="w-full lg:w-auto px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition font-semibold"
                  >
                    Select Seats
                  </button>
                  <button
                    onClick={() => navigate(`/group-booking/${flight.id}`)}
                    className="w-full lg:w-auto px-6 py-2 border border-blue-600 text-blue-600 rounded-xl hover:bg-blue-50 transition font-medium text-sm"
                  >
                    👥 Group Booking
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Dharma Message */}
        {!loading && flights.length > 0 && (
          <div className="text-center mt-12">
            <p className="text-gray-400 text-sm italic">
              "Every journey follows its natural order. Every seat has its perfect moment."
            </p>
          </div>
        )}

        {/* No Results Message */}
        {!loading && flights.length === 0 && !error && (
          <div className="text-center mt-12">
            <p className="text-gray-500 mb-4">Start your search to find available flights</p>
            <button
              onClick={() => navigate('/search')}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition"
            >
              Search Flights
            </button>
          </div>
        )}
      </motion.div>
    </PageWrapper>
  );
}
