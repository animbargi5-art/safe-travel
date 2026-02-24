import { useState } from 'react';
import { motion } from 'framer-motion';
import api from '../services/api';

export default function UltraFastBookingTest() {
  const [isTestRunning, setIsTestRunning] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [performanceStats, setPerformanceStats] = useState(null);

  const runUltraFastTest = async () => {
    setIsTestRunning(true);
    setTestResults(null);
    
    try {
      const startTime = performance.now();
      
      // Test ultra-fast booking
      const response = await api.post('/ultra-fast/book-seat', {
        flight_id: 2,
        seat_id: Math.floor(Math.random() * 180) + 1, // Random seat
        auto_confirm: false
      });
      
      const endTime = performance.now();
      const frontendTime = endTime - startTime;
      
      if (response.status === 200) {
        const result = response.data;
        setTestResults({
          success: true,
          bookingId: result.booking_id,
          seatNumber: result.seat_number,
          message: result.message,
          performance: {
            ...result.performance,
            frontend_time_ms: frontendTime,
            total_round_trip_ms: frontendTime
          }
        });
      }
      
    } catch (error) {
      setTestResults({
        success: false,
        error: error.response?.data?.detail || error.message,
        performance: {
          frontend_time_ms: performance.now() - performance.now()
        }
      });
    } finally {
      setIsTestRunning(false);
    }
  };

  const runLightningTest = async () => {
    setIsTestRunning(true);
    
    try {
      const startTime = performance.now();
      
      const response = await api.post('/ultra-fast/lightning-book', {
        flight_id: 2,
        seat_id: Math.floor(Math.random() * 180) + 1,
        auto_confirm: false
      });
      
      const endTime = performance.now();
      
      if (response.status === 200) {
        const result = response.data;
        setTestResults({
          success: true,
          type: 'lightning',
          bookingId: result.booking_id,
          seatNumber: result.seat_number,
          message: result.message,
          performance: {
            ...result.performance,
            frontend_time_ms: endTime - startTime
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

  const getPerformanceStats = async () => {
    try {
      const response = await api.get('/ultra-fast/performance-stats');
      setPerformanceStats(response.data);
    } catch (error) {
      console.error('Failed to get performance stats:', error);
    }
  };

  const runSpeedTest = async () => {
    setIsTestRunning(true);
    
    try {
      const response = await api.get('/ultra-fast/speed-test?iterations=50');
      setTestResults({
        success: true,
        type: 'speed_test',
        speedTest: response.data
      });
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
      className="bg-white rounded-xl p-6 shadow-lg max-w-4xl mx-auto"
    >
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          ⚡ Ultra-Fast Booking Performance Test
        </h2>
        <p className="text-gray-600">
          Test nanosecond-level booking performance and waitlist allocation
        </p>
      </div>

      {/* Test Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <button
          onClick={runUltraFastTest}
          disabled={isTestRunning}
          className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {isTestRunning ? '⏳ Testing...' : '🚀 Ultra-Fast Test'}
        </button>

        <button
          onClick={runLightningTest}
          disabled={isTestRunning}
          className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
        >
          {isTestRunning ? '⏳ Testing...' : '⚡ Lightning Test'}
        </button>

        <button
          onClick={runSpeedTest}
          disabled={isTestRunning}
          className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          {isTestRunning ? '⏳ Testing...' : '🏃‍♂️ Speed Test'}
        </button>

        <button
          onClick={getPerformanceStats}
          className="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          📊 Get Stats
        </button>
      </div>

      {/* Test Results */}
      {testResults && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`p-4 rounded-lg mb-6 ${
            testResults.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}
        >
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            {testResults.success ? '✅ Test Successful' : '❌ Test Failed'}
            {testResults.type && (
              <span className="text-sm bg-gray-100 px-2 py-1 rounded">
                {testResults.type}
              </span>
            )}
          </h3>

          {testResults.success ? (
            <div className="space-y-3">
              {testResults.bookingId && (
                <div>
                  <p><strong>Booking ID:</strong> {testResults.bookingId}</p>
                  <p><strong>Seat:</strong> {testResults.seatNumber}</p>
                  <p><strong>Message:</strong> {testResults.message}</p>
                </div>
              )}

              {testResults.performance && (
                <div className="bg-white p-3 rounded border">
                  <h4 className="font-medium mb-2">⚡ Performance Metrics</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    {testResults.performance.booking_time_ms && (
                      <div>
                        <div className="text-gray-600">Booking Time</div>
                        <div className="font-mono font-bold text-blue-600">
                          {testResults.performance.booking_time_ms.toFixed(2)}ms
                        </div>
                      </div>
                    )}
                    
                    {testResults.performance.db_time_microseconds && (
                      <div>
                        <div className="text-gray-600">DB Time</div>
                        <div className="font-mono font-bold text-purple-600">
                          {testResults.performance.db_time_microseconds.toFixed(0)}μs
                        </div>
                      </div>
                    )}
                    
                    {testResults.performance.total_time_ms && (
                      <div>
                        <div className="text-gray-600">Total Time</div>
                        <div className="font-mono font-bold text-green-600">
                          {testResults.performance.total_time_ms.toFixed(2)}ms
                        </div>
                      </div>
                    )}
                    
                    {testResults.performance.frontend_time_ms && (
                      <div>
                        <div className="text-gray-600">Frontend Time</div>
                        <div className="font-mono font-bold text-orange-600">
                          {testResults.performance.frontend_time_ms.toFixed(2)}ms
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {testResults.speedTest && (
                <div className="bg-white p-3 rounded border">
                  <h4 className="font-medium mb-2">🏃‍♂️ Speed Test Results</h4>
                  <div className="space-y-2 text-sm">
                    {Object.entries(testResults.speedTest.tests).map(([testName, data]) => (
                      <div key={testName} className="flex justify-between">
                        <span className="capitalize">{testName.replace('_', ' ')}</span>
                        <span className="font-mono">
                          {data.operations_per_second?.toFixed(0)} ops/sec
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-red-700">
              <strong>Error:</strong> {testResults.error}
            </div>
          )}
        </motion.div>
      )}

      {/* Performance Stats */}
      {performanceStats && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gray-50 p-4 rounded-lg"
        >
          <h3 className="font-semibold mb-3">📊 System Performance Stats</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            {performanceStats.ultra_fast_service && (
              <div>
                <h4 className="font-medium mb-2">Ultra-Fast Service</h4>
                <div className="space-y-1">
                  <div>Cache Size: {performanceStats.ultra_fast_service.cache_size?.seats || 0} seats</div>
                  <div>Active Locks: {performanceStats.ultra_fast_service.active_locks || 0}</div>
                  <div>Queue Size: {performanceStats.ultra_fast_service.queue_size || 0}</div>
                </div>
              </div>
            )}

            {performanceStats.database_optimizer && (
              <div>
                <h4 className="font-medium mb-2">Database Optimizer</h4>
                <div className="space-y-1">
                  <div>Pool Size: {performanceStats.database_optimizer.connection_pool?.size || 0}</div>
                  <div>Checked Out: {performanceStats.database_optimizer.connection_pool?.checked_out || 0}</div>
                  <div>Prepared Statements: {performanceStats.database_optimizer.prepared_statements || 0}</div>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h4 className="font-medium text-blue-800 mb-2">🎯 Performance Testing Guide</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li><strong>Ultra-Fast Test:</strong> Tests the complete ultra-fast booking pipeline</li>
          <li><strong>Lightning Test:</strong> Tests optimized database operations with prepared statements</li>
          <li><strong>Speed Test:</strong> Runs multiple iterations to measure average performance</li>
          <li><strong>Get Stats:</strong> Shows current system performance metrics</li>
        </ul>
      </div>
    </motion.div>
  );
}