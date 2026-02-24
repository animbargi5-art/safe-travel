import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../context/AuthContext';

export default function RealTimeBookingStatus({ bookingId, onStatusChange }) {
  const [status, setStatus] = useState('pending');
  const [lastUpdate, setLastUpdate] = useState(null);
  const [statusHistory, setStatusHistory] = useState([]);
  const { user } = useAuth();

  const { isConnected, sendMessage } = useWebSocket(
    'ws://localhost:8000/ws/notifications/{token}',
    {
      onMessage: (data) => {
        if (data.type === 'notification' && data.data?.booking_id === bookingId) {
          handleBookingUpdate(data);
        }
      }
    }
  );

  const handleBookingUpdate = (notification) => {
    const newStatus = getStatusFromNotification(notification);
    if (newStatus && newStatus !== status) {
      setStatus(newStatus);
      setLastUpdate(new Date());
      
      // Add to status history
      setStatusHistory(prev => [...prev, {
        status: newStatus,
        timestamp: new Date(),
        message: notification.message,
        type: notification.notification_type
      }]);

      // Notify parent component
      onStatusChange?.(newStatus, notification);
    }
  };

  const getStatusFromNotification = (notification) => {
    const typeToStatus = {
      'booking_confirmed': 'confirmed',
      'booking_cancelled': 'cancelled',
      'booking_expired': 'expired',
      'payment_completed': 'paid',
      'payment_failed': 'payment_failed'
    };
    
    return typeToStatus[notification.notification_type] || null;
  };

  const getStatusConfig = (currentStatus) => {
    const configs = {
      pending: {
        color: 'yellow',
        icon: '⏳',
        label: 'Pending',
        description: 'Waiting for payment...'
      },
      processing: {
        color: 'blue',
        icon: '🔄',
        label: 'Processing',
        description: 'Processing your payment...'
      },
      paid: {
        color: 'green',
        icon: '💳',
        label: 'Payment Complete',
        description: 'Payment processed successfully'
      },
      confirmed: {
        color: 'green',
        icon: '✅',
        label: 'Confirmed',
        description: 'Your booking is confirmed!'
      },
      cancelled: {
        color: 'red',
        icon: '❌',
        label: 'Cancelled',
        description: 'Booking has been cancelled'
      },
      expired: {
        color: 'gray',
        icon: '⏰',
        label: 'Expired',
        description: 'Booking time has expired'
      },
      payment_failed: {
        color: 'red',
        icon: '💳',
        label: 'Payment Failed',
        description: 'Payment could not be processed'
      }
    };

    return configs[currentStatus] || configs.pending;
  };

  const statusConfig = getStatusConfig(status);

  const colorClasses = {
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    blue: 'bg-blue-50 border-blue-200 text-blue-800',
    green: 'bg-green-50 border-green-200 text-green-800',
    red: 'bg-red-50 border-red-200 text-red-800',
    gray: 'bg-gray-50 border-gray-200 text-gray-800'
  };

  return (
    <div className="space-y-4">
      {/* Current Status */}
      <motion.div
        key={status}
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
        className={`rounded-lg border-2 p-4 ${colorClasses[statusConfig.color]}`}
      >
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{statusConfig.icon}</span>
          <div className="flex-1">
            <h3 className="font-semibold text-lg">{statusConfig.label}</h3>
            <p className="text-sm opacity-80">{statusConfig.description}</p>
            {lastUpdate && (
              <p className="text-xs opacity-60 mt-1">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </p>
            )}
          </div>
          
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-xs opacity-60">
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>
      </motion.div>

      {/* Progress Steps */}
      <div className="bg-white rounded-lg border p-4">
        <h4 className="font-medium text-gray-800 mb-3">Booking Progress</h4>
        <div className="space-y-3">
          {[
            { key: 'pending', label: 'Booking Created', icon: '📝' },
            { key: 'processing', label: 'Payment Processing', icon: '💳' },
            { key: 'paid', label: 'Payment Complete', icon: '✅' },
            { key: 'confirmed', label: 'Booking Confirmed', icon: '🎉' }
          ].map((step, index) => {
            const isCompleted = getStepStatus(step.key, status);
            const isCurrent = step.key === status;
            
            return (
              <div key={step.key} className="flex items-center space-x-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                  isCompleted ? 'bg-green-100 text-green-600' :
                  isCurrent ? 'bg-blue-100 text-blue-600' :
                  'bg-gray-100 text-gray-400'
                }`}>
                  {isCompleted ? '✓' : step.icon}
                </div>
                <span className={`flex-1 ${
                  isCompleted ? 'text-green-600 font-medium' :
                  isCurrent ? 'text-blue-600 font-medium' :
                  'text-gray-500'
                }`}>
                  {step.label}
                </span>
                {isCurrent && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Status History */}
      {statusHistory.length > 0 && (
        <div className="bg-white rounded-lg border p-4">
          <h4 className="font-medium text-gray-800 mb-3">Status History</h4>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {statusHistory.slice().reverse().map((entry, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span className="text-gray-600">{entry.message}</span>
                <span className="text-gray-400">
                  {entry.timestamp.toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Real-time Indicator */}
      <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
        <div className={`w-2 h-2 rounded-full ${
          isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
        }`} />
        <span>
          {isConnected ? 'Real-time updates active' : 'Connecting to live updates...'}
        </span>
      </div>
    </div>
  );
}

function getStepStatus(stepKey, currentStatus) {
  const statusOrder = ['pending', 'processing', 'paid', 'confirmed'];
  const currentIndex = statusOrder.indexOf(currentStatus);
  const stepIndex = statusOrder.indexOf(stepKey);
  
  // Handle error states
  if (['cancelled', 'expired', 'payment_failed'].includes(currentStatus)) {
    return stepIndex === 0; // Only first step is completed for error states
  }
  
  return stepIndex <= currentIndex;
}