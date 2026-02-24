import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import PageWrapper from '../components/PageWrapper';
import SectionTitle from '../components/ui/SectionTitle';
import NotificationCenter from '../components/NotificationCenter';
import RealTimeBookingStatus from '../components/RealTimeBookingStatus';
import { useNotifications } from '../hooks/useWebSocket';
import { useAuth } from '../context/AuthContext';

export default function RealTimeDemo() {
  const { isAuthenticated } = useAuth();
  const [demoBookingId] = useState(12345);
  const [connectionStats, setConnectionStats] = useState(null);
  
  const {
    notifications,
    unreadCount,
    isConnected,
    sendTestNotification,
    connectionState
  } = useNotifications();

  useEffect(() => {
    // Fetch connection stats periodically
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/ws/connections/stats');
        const stats = await response.json();
        setConnectionStats(stats);
      } catch (error) {
        console.error('Error fetching connection stats:', error);
      }
    };

    if (isConnected) {
      fetchStats();
      const interval = setInterval(fetchStats, 10000); // Update every 10 seconds
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const handleStatusChange = (newStatus, notification) => {
    console.log('Booking status changed:', newStatus, notification);
  };

  if (!isAuthenticated) {
    return (
      <PageWrapper>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Authentication Required</h2>
          <p className="text-gray-600">Please log in to see real-time notifications demo.</p>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <SectionTitle
        title="Real-time Notifications Demo"
        subtitle="Experience live updates and instant notifications"
      />

      <div className="space-y-8">
        {/* Connection Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Connection Status</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${
                isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`} />
              <div className="text-sm font-medium text-gray-800">
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
              <div className="text-xs text-gray-500 capitalize">{connectionState}</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{unreadCount}</div>
              <div className="text-sm text-gray-600">Unread</div>
              <div className="text-xs text-gray-500">Notifications</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{notifications.length}</div>
              <div className="text-sm text-gray-600">Total</div>
              <div className="text-xs text-gray-500">Received</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {connectionStats?.connected_users || 0}
              </div>
              <div className="text-sm text-gray-600">Users</div>
              <div className="text-xs text-gray-500">Online</div>
            </div>
          </div>
        </motion.div>

        {/* Demo Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Demo Controls</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={sendTestNotification}
              disabled={!isConnected}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              🧪 Send Test Notification
            </button>
            
            <button
              onClick={() => {
                // Simulate booking confirmation
                if (isConnected) {
                  // This would normally come from the backend
                  console.log('Simulating booking confirmation...');
                }
              }}
              disabled={!isConnected}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              ✅ Simulate Booking Confirmed
            </button>
            
            <button
              onClick={() => {
                // Simulate payment completion
                if (isConnected) {
                  console.log('Simulating payment completion...');
                }
              }}
              disabled={!isConnected}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              💳 Simulate Payment Complete
            </button>
          </div>
          
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              <strong>How it works:</strong> This demo shows real-time WebSocket notifications. 
              In a real booking flow, these notifications are automatically triggered by payment 
              completions, booking confirmations, flight delays, and other system events.
            </p>
          </div>
        </motion.div>

        {/* Real-time Booking Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Live Booking Status</h3>
          <RealTimeBookingStatus
            bookingId={demoBookingId}
            onStatusChange={handleStatusChange}
          />
        </motion.div>

        {/* Notification Center Demo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Notification Center</h3>
          <div className="text-center">
            <p className="text-gray-600 mb-4">
              Click the notification bell in the top navigation to see the notification center in action.
            </p>
            <div className="inline-block">
              <NotificationCenter />
            </div>
          </div>
        </motion.div>

        {/* Recent Notifications */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Notifications</h3>
          
          {notifications.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <span className="text-4xl mb-2 block">🔔</span>
              <p>No notifications yet</p>
              <p className="text-sm">Send a test notification to see it appear here</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {notifications.slice(0, 5).map((notification) => (
                <div key={notification.id} className="border rounded-lg p-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-800">{notification.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-gray-500">
                          {new Date(notification.timestamp).toLocaleTimeString()}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          notification.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                          notification.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                          notification.priority === 'medium' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {notification.priority}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Technical Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-blue-50 border border-blue-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold text-blue-800 mb-4">🚀 Real-time Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-700">
            <div>
              <h4 className="font-medium mb-2">Backend Features:</h4>
              <ul className="space-y-1">
                <li>• WebSocket connection management</li>
                <li>• Real-time notification service</li>
                <li>• Background monitoring tasks</li>
                <li>• Event-driven notifications</li>
                <li>• Connection health monitoring</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Frontend Features:</h4>
              <ul className="space-y-1">
                <li>• Persistent WebSocket connections</li>
                <li>• Automatic reconnection handling</li>
                <li>• Browser notification integration</li>
                <li>• Real-time status updates</li>
                <li>• Responsive notification UI</li>
              </ul>
            </div>
          </div>
        </motion.div>

        {/* Dharma Message */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-green-50 border border-green-200 rounded-lg p-6 text-center"
        >
          <span className="text-3xl mb-3 block">🧘</span>
          <p className="text-green-800 italic">
            "In the flow of instant connection, mindful communication creates harmony between technology and human experience."
          </p>
          <p className="text-green-600 text-sm mt-2">
            - Safe Travel Real-time Philosophy
          </p>
        </motion.div>
      </div>
    </PageWrapper>
  );
}