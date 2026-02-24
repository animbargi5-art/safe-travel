import { useState } from 'react';
import { motion } from 'framer-motion';

export default function AutoSeatAllocation({ 
  allocationOptions, 
  onAutoAllocate, 
  isLoading 
}) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [preferences, setPreferences] = useState({
    seatClass: 'ECONOMY',
    position: 'ANY',
    strategy: 'BEST_AVAILABLE'
  });

  const handleQuickAllocate = (position, seatClass = 'ECONOMY') => {
    onAutoAllocate(position, seatClass);
  };

  const handleAdvancedAllocate = () => {
    onAutoAllocate(preferences.position, preferences.seatClass, preferences.strategy);
  };

  if (!allocationOptions) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 shadow-sm border border-blue-100"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
            🤖 Smart Seat Selection
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Let our AI find the perfect seat for your journey
          </p>
        </div>
        <div className="text-right text-sm text-gray-500">
          <div>{allocationOptions.total_available} seats available</div>
        </div>
      </div>

      {/* Quick Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <button
          onClick={() => handleQuickAllocate("ANY", "ECONOMY")}
          disabled={isLoading}
          className="group p-4 bg-white rounded-lg border-2 border-blue-200 hover:border-blue-400 transition-all disabled:opacity-50"
        >
          <div className="text-2xl mb-2">🎯</div>
          <div className="font-medium text-gray-800">Best Available</div>
          <div className="text-xs text-gray-500 mt-1">
            Optimal seat based on location and class
          </div>
        </button>

        <button
          onClick={() => handleQuickAllocate("WINDOW", "ECONOMY")}
          disabled={isLoading}
          className="group p-4 bg-white rounded-lg border-2 border-green-200 hover:border-green-400 transition-all disabled:opacity-50"
        >
          <div className="text-2xl mb-2">🪟</div>
          <div className="font-medium text-gray-800">Window Seat</div>
          <div className="text-xs text-gray-500 mt-1">
            Perfect for views and privacy
          </div>
        </button>

        <button
          onClick={() => handleQuickAllocate("AISLE", "ECONOMY")}
          disabled={isLoading}
          className="group p-4 bg-white rounded-lg border-2 border-purple-200 hover:border-purple-400 transition-all disabled:opacity-50"
        >
          <div className="text-2xl mb-2">🚶</div>
          <div className="font-medium text-gray-800">Aisle Seat</div>
          <div className="text-xs text-gray-500 mt-1">
            Easy access and leg room
          </div>
        </button>
      </div>

      {/* Recommendations */}
      {allocationOptions.recommendations && allocationOptions.recommendations.length > 0 && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-700 mb-3">🌟 AI Recommendations</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {allocationOptions.recommendations.slice(0, 3).map((rec, index) => (
              <button
                key={index}
                onClick={() => handleQuickAllocate(rec.seat.position, rec.seat.seat_class)}
                disabled={isLoading}
                className="text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all disabled:opacity-50"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium text-gray-800">
                      Seat {rec.seat.seat_number}
                    </div>
                    <div className="text-sm text-gray-600">
                      {rec.description}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {rec.seat.seat_class} • {rec.seat.position}
                    </div>
                  </div>
                  <div className="text-blue-600 text-sm">→</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Advanced Options Toggle */}
      <div className="border-t border-gray-200 pt-4">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
        >
          {showAdvanced ? '▼' : '▶'} Advanced Options
        </button>

        {showAdvanced && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Seat Class
              </label>
              <select
                value={preferences.seatClass}
                onChange={(e) => setPreferences(prev => ({...prev, seatClass: e.target.value}))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="ANY">Any Class</option>
                <option value="ECONOMY">Economy</option>
                <option value="BUSINESS">Business</option>
                <option value="FIRST">First Class</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Position Preference
              </label>
              <select
                value={preferences.position}
                onChange={(e) => setPreferences(prev => ({...prev, position: e.target.value}))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="ANY">Any Position</option>
                <option value="WINDOW">Window</option>
                <option value="AISLE">Aisle</option>
                <option value="MIDDLE">Middle</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Strategy
              </label>
              <select
                value={preferences.strategy}
                onChange={(e) => setPreferences(prev => ({...prev, strategy: e.target.value}))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="BEST_AVAILABLE">Best Available</option>
                <option value="FRONT_TO_BACK">Front to Back</option>
                <option value="BACK_TO_FRONT">Back to Front</option>
                <option value="RANDOM">Random</option>
              </select>
            </div>

            <div className="md:col-span-3">
              <button
                onClick={handleAdvancedAllocate}
                disabled={isLoading}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
              >
                {isLoading ? "Allocating..." : "Apply Advanced Selection"}
              </button>
            </div>
          </motion.div>
        )}
      </div>

      {/* Statistics */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm">
        <div className="bg-white rounded-lg p-3">
          <div className="font-semibold text-gray-800">
            {allocationOptions.by_position?.WINDOW || 0}
          </div>
          <div className="text-gray-500">Window</div>
        </div>
        <div className="bg-white rounded-lg p-3">
          <div className="font-semibold text-gray-800">
            {allocationOptions.by_position?.AISLE || 0}
          </div>
          <div className="text-gray-500">Aisle</div>
        </div>
        <div className="bg-white rounded-lg p-3">
          <div className="font-semibold text-gray-800">
            {allocationOptions.by_class?.BUSINESS || 0}
          </div>
          <div className="text-gray-500">Business</div>
        </div>
        <div className="bg-white rounded-lg p-3">
          <div className="font-semibold text-gray-800">
            {allocationOptions.by_class?.FIRST || 0}
          </div>
          <div className="text-gray-500">First</div>
        </div>
      </div>

      {/* Dharma message */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg text-center">
        <p className="text-blue-800 text-sm italic">
          "The right seat appears when the intention is clear and the timing is perfect."
        </p>
      </div>
    </motion.div>
  );
}