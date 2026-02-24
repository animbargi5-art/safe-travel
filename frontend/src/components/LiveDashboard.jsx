import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function LiveDashboard() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [activityStream, setActivityStream] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [performanceTest, setPerformanceTest] = useState(null);
  const wsRef = useRef(null);
  const intervalRef = useRef(null);

  // Check if user is admin
  const isAdmin = user?.email === 'test@safetravelapp.com';

  useEffect(() => {
    if (!user) return;

    // Initial data fetch
    fetchDashboardData();
    fetchActivityStream();

    // Set up WebSocket connection for real-time updates
    connectWebSocket();

    // Set up periodic refresh
    intervalRef.current = setInterval(() => {
      fetchDashboardData();
      fetchActivityStream();
    }, 2000); // Update every 2 seconds

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [user]);

  const connectWebSocket = () => {
    if (!user) return;

    try {
      const wsUrl = `ws://localhost:8000/live-monitoring/ws/${user.id}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        console.log('🔄 Connected to live monitoring WebSocket');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'DASHBOARD_UPDATE') {
            setDashboardData(message.data);
          } else if (message.type === 'ACTIVITY_UPDATE') {
            setActivityStream(prev => [message.data, ...prev.slice(0, 19)]);
          }
        } catch (error) {
          console.error('WebSocket message error:', error);
        }
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        console.log('🔌 Disconnected from live monitoring WebSocket');
        
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/live-monitoring/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const fetchActivityStream = async () => {
    try {
      const response = await api.get('/live-monitoring/activity-stream');
      setActivityStream(response.data.activities);
    } catch (error) {
      console.error('Failed to fetch activity stream:', error);
    }
  };

  const runPerformanceTest = async () => {
    if (!isAdmin) return;

    try {
      setPerformanceTest({ running: true });
      const response = await api.get('/live-monitoring/performance-test?iterations=5');
      setPerformanceTest({ running: false, results: response.data });
      
      // Refresh data after test
      setTimeout(() => {
        fetchDashboardData();
        fetchActivityStream();
      }, 1000);
      
    } catch (error) {
      console.error('Performance test failed:', error);
      setPerformanceTest({ running: false, error: error.message });
    }
  };

  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading live dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">
            {isAdmin ? '🔍 Admin Live Dashboard' : '📊 Live System Status'}
          </h2>
          <p className="text-gray-600">
            Real-time backend performance and activity monitoring
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Connection Status */}
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'Live Connected' : 'Disconnected'}
            </span>
          </div>
          
          {/* Performance Test Button (Admin Only) */}
          {isAdmin && (
            <button
              onClick={runPerformanceTest}
              disabled={performanceTest?.running}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
            >
              {performanceTest?.running ? '⏳ Testing...' : '🚀 Run Test'}
            </button>
          )}
        </div>
      </div>

      {/* Admin Dashboard */}
      {isAdmin && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* System Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200"
          >
            <h3 className="font-semibold text-blue-800 mb-4">📊 System Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-blue-700">Total Bookings:</span>
                <span className="font-bold text-blue-800">
                  {dashboardData.system_stats?.total_bookings || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700">Success Rate:</span>
                <span className="font-bold text-green-600">
                  {dashboardData.system_stats?.success_rate?.toFixed(1) || 0}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700">Active Users:</span>
                <span className="font-bold text-blue-800">
                  {dashboardData.system_stats?.active_users || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700">Waitlist Allocations:</span>
                <span className="font-bold text-purple-600">
                  {dashboardData.system_stats?.waitlist_allocations || 0}
                </span>
              </div>
            </div>
          </motion.div>

          {/* Performance Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border border-green-200"
          >
            <h3 className="font-semibold text-green-800 mb-4">⚡ Performance</h3>
            <div className="space-y-3">
              <div>
                <div className="text-green-700 text-sm">Avg Booking Time:</div>
                <div className="font-bold text-green-800">
                  {dashboardData.performance_metrics?.avg_booking_time_microseconds?.toFixed(2) || 0}μs
                </div>
              </div>
              <div>
                <div className="text-green-700 text-sm">Throughput:</div>
                <div className="font-bold text-green-800">
                  {Math.round(dashboardData.performance_metrics?.bookings_per_second || 0).toLocaleString()}/sec
                </div>
              </div>
              <div>
                <div className="text-green-700 text-sm">Min Time:</div>
                <div className="font-bold text-green-600">
                  {(dashboardData.performance_metrics?.min_booking_time_ns / 1000)?.toFixed(2) || 0}μs
                </div>
              </div>
            </div>
          </motion.div>

          {/* Nanosecond Engine */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200"
          >
            <h3 className="font-semibold text-purple-800 mb-4">🚀 Nanosecond Engine</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-purple-700">Status:</span>
                <span className="font-bold text-green-600">
                  {dashboardData.nanosecond_engine?.status || 'UNKNOWN'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-purple-700">Available Seats:</span>
                <span className="font-bold text-purple-800">
                  {dashboardData.nanosecond_engine?.available_seats || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-purple-700">Bookings Made:</span>
                <span className="font-bold text-purple-800">
                  {dashboardData.nanosecond_engine?.booking_counter || 0}
                </span>
              </div>
            </div>
          </motion.div>

          {/* Real-time Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl border border-orange-200"
          >
            <h3 className="font-semibold text-orange-800 mb-4">🔄 Live Activity</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-orange-700">Last Hour:</span>
                <span className="font-bold text-orange-800">
                  {dashboardData.booking_analytics?.total_recent_activities || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-orange-700">Activity Rate:</span>
                <span className="font-bold text-orange-800">
                  {dashboardData.booking_analytics?.activity_rate_per_minute?.toFixed(1) || 0}/min
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* User Dashboard (Non-Admin) */}
      {!isAdmin && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200"
          >
            <h3 className="font-semibold text-blue-800 mb-4">🏥 System Health</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-blue-700">Status:</span>
                <span className="font-bold text-green-600">
                  {dashboardData.system_health?.status || 'UNKNOWN'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700">Booking System:</span>
                <span className="font-bold text-green-600">
                  {dashboardData.system_health?.booking_system_status || 'UNKNOWN'}
                </span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border border-green-200"
          >
            <h3 className="font-semibold text-green-800 mb-4">⚡ Booking Speed</h3>
            <div className="space-y-3">
              <div>
                <div className="text-green-700 text-sm">Performance Level:</div>
                <div className="font-bold text-green-800">
                  {dashboardData.booking_speed?.performance_level || 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-green-700 text-sm">Avg Speed:</div>
                <div className="font-bold text-green-800">
                  {dashboardData.booking_speed?.avg_speed_microseconds?.toFixed(2) || 'N/A'}μs
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200"
          >
            <h3 className="font-semibold text-purple-800 mb-4">👤 Your Activity</h3>
            <div className="space-y-2">
              {dashboardData.user_activity?.slice(0, 3).map((activity, index) => (
                <div key={index} className="text-sm">
                  <div className="font-medium text-purple-800">
                    {activity.type.replace('_', ' ')}
                  </div>
                  <div className="text-purple-600 text-xs">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              )) || <div className="text-purple-600 text-sm">No recent activity</div>}
            </div>
          </motion.div>
        </div>
      )}

      {/* Performance Test Results */}
      {performanceTest?.results && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white p-6 rounded-xl border-2 border-purple-200"
        >
          <h3 className="font-bold text-lg mb-4">🚀 Performance Test Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-purple-600 text-sm">Avg Booking Time</div>
              <div className="font-bold text-purple-800 text-xl">
                {performanceTest.results.avg_booking_time_microseconds?.toFixed(2) || 0}μs
              </div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-green-600 text-sm">Throughput</div>
              <div className="font-bold text-green-800 text-xl">
                {Math.round(performanceTest.results.bookings_per_second || 0).toLocaleString()}/sec
              </div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-blue-600 text-sm">Avg Lookup Time</div>
              <div className="font-bold text-blue-800 text-xl">
                {performanceTest.results.avg_lookup_time_microseconds?.toFixed(2) || 0}μs
              </div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-orange-600 text-sm">Iterations</div>
              <div className="font-bold text-orange-800 text-xl">
                {performanceTest.results.iterations || 0}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Live Activity Stream */}
      {activityStream.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white p-6 rounded-xl border border-gray-200"
        >
          <h3 className="font-bold text-lg mb-4">
            📊 {isAdmin ? 'Live System Activity' : 'Your Recent Activity'}
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            <AnimatePresence>
              {activityStream.slice(0, 10).map((activity, index) => (
                <motion.div
                  key={`${activity.timestamp}-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="font-medium text-gray-800">
                      {getActivityIcon(activity.type)} {activity.type.replace('_', ' ')}
                    </div>
                    <div className="text-sm text-gray-600">
                      {activity.details && Object.keys(activity.details).length > 0 && (
                        <span>
                          {activity.details.seat_number && `Seat: ${activity.details.seat_number}`}
                          {activity.details.booking_time_microseconds && 
                            ` • ${activity.details.booking_time_microseconds.toFixed(2)}μs`}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function getActivityIcon(type) {
  const icons = {
    'BOOKING_SUCCESS': '✅',
    'BOOKING_FAILED': '❌',
    'BOOKING_CANCELLED': '🔄',
    'WAITLIST_ALLOCATED': '🎯',
    'PERFORMANCE_TEST_BOOKING': '🚀',
    'PERFORMANCE_TEST_COMPLETED': '📊',
    'SEAT_LOOKUP': '👀',
    'NANOSECOND_BOOKING': '⚡',
    'SYSTEM_STATUS': '🔍',
    'PERFORMANCE_UPDATE': '📈'
  };
  
  return icons[type] || '📝';
}