import { useState } from 'react';
import { motion } from 'framer-motion';
import api from '../services/api';

export default function NanosecondBookingTest() {
  const [isTestRunning, setIsTestRunning] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [benchmarkResults, setBenchmarkResults] = useState(null);

  const runNanosecondBooking = async () => {
    setIsTestRunning(true);
    setTestResults(null);
    
    try {
      const frontendStart = performance.now();
      
      // Test nanosecond booking
      const response = await api.post('/nanosecond/book', {
        flight_id: 2,
        seat_id: Math.floor(Math.random() * 180) + 1
      });
      
      const frontendEnd = performance.now();
      const frontendTime = frontendEnd - frontendStart;
      
      if (response.status === 200) {
        const result = response.data;
        setTestResults({
          success: true,
          type: 'nanosecond_booking',
          bookingId: result.booking_id,
          seatNumber: result.seat_number,
          seatClass: result.seat_class,
          message: result.message,
          performance: {
            ...result.performance,
            frontend_time_ms: frontendTime,
            network_overhead_ms: frontendTime - (result.performance.total_api_microseconds / 1000)
          }
        });
      }
      
    } catch (error) {
      setTestResults({
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setIsTestRunning(false);
    }
  };

  const runNanosecondCancel = async () => {
    setIsTestRunning(true);
    
    try {
      // First create a booking to cancel
      const bookResponse = await api.post('/nanosecond/book', {
        flight_id: 2,
        seat_id: Math.floor(Math.random() * 180) + 1
      });
      
      if (bookResponse.status === 200) {
        const bookingId = bookResponse.data.booking_id;
        
        // Now test nanosecond cancellation
        const frontendStart = performance.now();
        
        const cancelResponse = await api.post('/nanosecond/cancel', {
          booking_id: bookingId
        });
        
        const frontendEnd = performance.now();
        
        if (cancelResponse.status === 200) {
          const result = cancelResponse.data;
          setTestResults({
            success: true,
            type: 'nanosecond_cancel',
            message: result.message,
            waitlistAllocation: result.waitlist_allocation,
            performance: {
              ...result.performance,
              frontend_time_ms: frontendEnd - frontendStart
            }
          });
        }
      }
      
    } catch (error) {
      setTestResults({
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setIsTestRunning(false);
    }
  };

  const runNanosecondBenchmark = async () => {
    setIsTestRunning(true);
    setBenchmarkResults(null);
    
    try {
      const response = await api.post('/nanosecond/benchmark?iterations=100');
      
      if (response.status === 200) {
        setBenchmarkResults(response.data);
      }
      
    } catch (error) {
      setTestResults({
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setIsTestRunning(false);
    }
  };

  const runStressTest = async () => {
    setIsTestRunning(true);
    
    try {
      const response = await api.post('/nanosecond/stress-test?concurrent_operations=100');
      
      if (response.status === 200) {
        setTestResults({
          success: true,
          type: 'stress_test',
          stressResults: response.data.stress_test_results
        });
      }
      
    } catch (error) {
      setTestResults({
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setIsTestRunning(false);
    }
  };

  const getInstantSeats = async () => {
    setIsTestRunning(true);
    
    try {
      const frontendStart = performance.now();
      
      const response = await api.get('/nanosecond/seats/2');
      
      const frontendEnd = performance.now();
      
      if (response.status === 200) {
        const result = response.data;
        setTestResults({
          success: true,
          type: 'instant_seats',
          seatCount: result.count,
          performance: {
            ...result.performance,
            frontend_time_ms: frontendEnd - frontendStart
          }
        });
      }
      
    } catch (error) {
      setTestResults({
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setIsTestRunning(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-6 shadow-lg max-w-6xl mx-auto border border-purple-200"
    >
      <div className="text-center mb-6">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
          🚀 NANOSECOND BOOKING ENGINE
        </h2>
        <p className="text-gray-700 font-medium">
          True nanosecond performance with pure in-memory operations
        </p>
        <div className="mt-2 inline-flex items-center gap-2 bg-purple-100 px-3 py-1 rounded-full text-sm">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span className="text-purple-700 font-medium">HYPER-OPTIMIZED ENGINE ACTIVE</span>
        </div>
      </div>

      {/* Test Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
        <button
          onClick={runNanosecondBooking}
          disabled={isTestRunning}
          className="px-4 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 disabled:opacity-50 transition-all transform hover:scale-105 shadow-lg"
        >
          {isTestRunning ? '⏳' : '🚀'} Nanosecond Book
        </button>

        <button
          onClick={runNanosecondCancel}
          disabled={isTestRunning}
          className="px-4 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 disabled:opacity-50 transition-all transform hover:scale-105 shadow-lg"
        >
          {isTestRunning ? '⏳' : '⚡'} Instant Cancel
        </button>

        <button
          onClick={getInstantSeats}
          disabled={isTestRunning}
          className="px-4 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 disabled:opacity-50 transition-all transform hover:scale-105 shadow-lg"
        >
          {isTestRunning ? '⏳' : '💨'} Instant Seats
        </button>

        <button
          onClick={runNanosecondBenchmark}
          disabled={isTestRunning}
          className="px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 transition-all transform hover:scale-105 shadow-lg"
        >
          {isTestRunning ? '⏳' : '📊'} Benchmark
        </button>

        <button
          onClick={runStressTest}
          disabled={isTestRunning}
          className="px-4 py-3 bg-gradient-to-r from-orange-600 to-orange-700 text-white rounded-lg hover:from-orange-700 hover:to-orange-800 disabled:opacity-50 transition-all transform hover:scale-105 shadow-lg"
        >
          {isTestRunning ? '⏳' : '💪'} Stress Test
        </button>
      </div>

      {/* Test Results */}
      {testResults && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`p-6 rounded-xl mb-6 border-2 ${
            testResults.success 
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300' 
              : 'bg-gradient-to-r from-red-50 to-pink-50 border-red-300'
          }`}
        >
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            {testResults.success ? '✅ NANOSECOND SUCCESS' : '❌ Test Failed'}
            {testResults.type && (
              <span className="text-sm bg-white px-3 py-1 rounded-full border">
                {testResults.type.replace('_', ' ').toUpperCase()}
              </span>
            )}
          </h3>

          {testResults.success ? (
            <div className="space-y-4">
              {/* Booking Results */}
              {testResults.bookingId && (
                <div className="bg-white p-4 rounded-lg border">
                  <h4 className="font-semibold mb-2">🎯 Booking Details</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <div className="text-gray-600">Booking ID</div>
                      <div className="font-mono font-bold">{testResults.bookingId}</div>
                    </div>
                    <div>
                      <div className="text-gray-600">Seat</div>
                      <div className="font-mono font-bold">{testResults.seatNumber}</div>
                    </div>
                    <div>
                      <div className="text-gray-600">Class</div>
                      <div className="font-mono font-bold">{testResults.seatClass}</div>
                    </div>
                    <div>
                      <div className="text-gray-600">Status</div>
                      <div className="font-mono font-bold text-green-600">BOOKED</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Performance Metrics */}
              {testResults.performance && (
                <div className="bg-white p-4 rounded-lg border">
                  <h4 className="font-semibold mb-3">⚡ NANOSECOND PERFORMANCE</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {testResults.performance.core_booking_ns && (
                      <div className="text-center p-3 bg-purple-50 rounded-lg">
                        <div className="text-gray-600 text-xs">Core Booking</div>
                        <div className="font-mono font-bold text-purple-600 text-lg">
                          {testResults.performance.core_booking_ns.toLocaleString()}ns
                        </div>
                        <div className="text-xs text-gray-500">
                          {testResults.performance.core_booking_microseconds?.toFixed(2)}μs
                        </div>
                      </div>
                    )}
                    
                    {testResults.performance.core_lookup_ns && (
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-gray-600 text-xs">Memory Lookup</div>
                        <div className="font-mono font-bold text-green-600 text-lg">
                          {testResults.performance.core_lookup_ns.toLocaleString()}ns
                        </div>
                        <div className="text-xs text-gray-500">
                          {testResults.performance.core_lookup_microseconds?.toFixed(2)}μs
                        </div>
                      </div>
                    )}
                    
                    {testResults.performance.operations_per_second && (
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="text-gray-600 text-xs">Throughput</div>
                        <div className="font-mono font-bold text-blue-600 text-lg">
                          {Math.round(testResults.performance.operations_per_second).toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-500">ops/second</div>
                      </div>
                    )}
                    
                    {testResults.performance.frontend_time_ms && (
                      <div className="text-center p-3 bg-orange-50 rounded-lg">
                        <div className="text-gray-600 text-xs">Total Time</div>
                        <div className="font-mono font-bold text-orange-600 text-lg">
                          {testResults.performance.frontend_time_ms.toFixed(2)}ms
                        </div>
                        <div className="text-xs text-gray-500">including network</div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Stress Test Results */}
              {testResults.stressResults && (
                <div className="bg-white p-4 rounded-lg border">
                  <h4 className="font-semibold mb-3">💪 Stress Test Results</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="text-center">
                      <div className="text-gray-600">Success Rate</div>
                      <div className="font-bold text-green-600 text-xl">
                        {testResults.stressResults.success_rate?.toFixed(1)}%
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-600">Avg Time</div>
                      <div className="font-mono font-bold text-blue-600">
                        {testResults.stressResults.avg_operation_time_microseconds?.toFixed(2)}μs
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-600">Min Time</div>
                      <div className="font-mono font-bold text-purple-600">
                        {testResults.stressResults.min_operation_time_microseconds?.toFixed(2)}μs
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-600">Throughput</div>
                      <div className="font-bold text-orange-600">
                        {Math.round(testResults.stressResults.throughput || 0).toLocaleString()}/sec
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Seat Count */}
              {testResults.seatCount !== undefined && (
                <div className="bg-white p-4 rounded-lg border">
                  <h4 className="font-semibold mb-2">💺 Available Seats</h4>
                  <div className="text-2xl font-bold text-green-600">
                    {testResults.seatCount} seats available
                  </div>
                </div>
              )}

              {/* Message */}
              {testResults.message && (
                <div className="bg-gradient-to-r from-purple-100 to-blue-100 p-4 rounded-lg border border-purple-200">
                  <div className="font-medium text-purple-800">
                    {testResults.message}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-red-700 bg-white p-4 rounded-lg">
              <strong>Error:</strong> {testResults.error}
            </div>
          )}
        </motion.div>
      )}

      {/* Benchmark Results */}
      {benchmarkResults && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white p-6 rounded-xl border-2 border-blue-200"
        >
          <h3 className="font-bold text-lg mb-4">📊 Nanosecond Benchmark Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(benchmarkResults.tests).map(([testName, data]) => (
              <div key={testName} className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3 capitalize">
                  {testName.replace('_', ' ')}
                </h4>
                <div className="space-y-2 text-sm">
                  {data.avg_time_microseconds && (
                    <div className="flex justify-between">
                      <span>Avg Time:</span>
                      <span className="font-mono font-bold">
                        {data.avg_time_microseconds.toFixed(2)}μs
                      </span>
                    </div>
                  )}
                  {data.min_time_microseconds && (
                    <div className="flex justify-between">
                      <span>Min Time:</span>
                      <span className="font-mono font-bold text-green-600">
                        {data.min_time_microseconds.toFixed(2)}μs
                      </span>
                    </div>
                  )}
                  {data.bookings_per_second && (
                    <div className="flex justify-between">
                      <span>Throughput:</span>
                      <span className="font-bold text-blue-600">
                        {Math.round(data.bookings_per_second).toLocaleString()}/sec
                      </span>
                    </div>
                  )}
                  {data.operations_per_second && (
                    <div className="flex justify-between">
                      <span>Ops/Sec:</span>
                      <span className="font-bold text-purple-600">
                        {Math.round(data.operations_per_second).toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Performance Highlights */}
      <div className="mt-6 bg-gradient-to-r from-purple-100 to-blue-100 p-6 rounded-xl border border-purple-200">
        <h4 className="font-bold text-purple-800 mb-3">🚀 Nanosecond Engine Features</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h5 className="font-semibold text-purple-700 mb-2">In-Memory Operations:</h5>
            <ul className="space-y-1 text-purple-600">
              <li>• Pure memory-based seat tracking</li>
              <li>• Atomic thread-safe operations</li>
              <li>• Zero database queries for booking</li>
              <li>• Instant waitlist processing</li>
            </ul>
          </div>
          <div>
            <h5 className="font-semibold text-purple-700 mb-2">Performance Optimizations:</h5>
            <ul className="space-y-1 text-purple-600">
              <li>• Nanosecond-level timing precision</li>
              <li>• Async database persistence</li>
              <li>• Lock-free data structures</li>
              <li>• Pre-compiled SQL statements</li>
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  );
}