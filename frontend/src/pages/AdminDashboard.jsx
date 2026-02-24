import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import PageWrapper from '../components/PageWrapper';
import api from '../services/api';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/admin/dashboard/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <PageWrapper>
        <LoadingState message="Loading admin dashboard..." />
      </PageWrapper>
    );
  }

  if (error) {
    return (
      <PageWrapper>
        <EmptyState 
          title="Dashboard Error"
          message={error}
          actionText="Retry"
          onAction={loadDashboardStats}
        />
      </PageWrapper>
    );
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const StatCard = ({ title, value, subtitle, icon, color = 'blue' }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white rounded-xl shadow-sm border-l-4 border-${color}-500 p-6`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`text-3xl text-${color}-500`}>
          {icon}
        </div>
      </div>
    </motion.div>
  );

  const TabButton = ({ id, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`px-6 py-3 rounded-lg font-medium transition ${
        isActive
          ? 'bg-blue-600 text-white'
          : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
      }`}
    >
      {label}
    </button>
  );

  return (
    <PageWrapper>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🛠️ Admin Dashboard
          </h1>
          <p className="text-gray-600">
            Manage your flight booking system with mindful oversight
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-2 mb-8 bg-gray-100 p-2 rounded-lg w-fit">
          <TabButton
            id="overview"
            label="Overview"
            isActive={activeTab === 'overview'}
            onClick={setActiveTab}
          />
          <TabButton
            id="flights"
            label="Flights"
            isActive={activeTab === 'flights'}
            onClick={setActiveTab}
          />
          <TabButton
            id="bookings"
            label="Bookings"
            isActive={activeTab === 'bookings'}
            onClick={setActiveTab}
          />
          <TabButton
            id="users"
            label="Users"
            isActive={activeTab === 'users'}
            onClick={setActiveTab}
          />
          <TabButton
            id="analytics"
            label="Analytics"
            isActive={activeTab === 'analytics'}
            onClick={setActiveTab}
          />
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-8"
          >
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Total Users"
                value={stats.total_users.toLocaleString()}
                icon="👥"
                color="blue"
              />
              <StatCard
                title="Total Flights"
                value={stats.total_flights.toLocaleString()}
                icon="✈️"
                color="green"
              />
              <StatCard
                title="Total Bookings"
                value={stats.total_bookings.toLocaleString()}
                subtitle={`${stats.confirmed_bookings} confirmed`}
                icon="📋"
                color="purple"
              />
              <StatCard
                title="Total Revenue"
                value={formatCurrency(stats.total_revenue)}
                subtitle={`${formatCurrency(stats.recent_revenue)} this month`}
                icon="💰"
                color="yellow"
              />
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Popular Routes */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  🔥 Popular Routes
                </h3>
                <div className="space-y-3">
                  {stats.popular_routes.slice(0, 5).map((route, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-gray-700">{route.route}</span>
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium">
                        {route.bookings} bookings
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  ⚡ Quick Actions
                </h3>
                <div className="space-y-3">
                  <button
                    onClick={() => setActiveTab('flights')}
                    className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition"
                  >
                    <div className="font-medium text-gray-900">Manage Flights</div>
                    <div className="text-sm text-gray-500">Add, edit, or remove flights</div>
                  </button>
                  <button
                    onClick={() => setActiveTab('bookings')}
                    className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition"
                  >
                    <div className="font-medium text-gray-900">View Bookings</div>
                    <div className="text-sm text-gray-500">Monitor and manage bookings</div>
                  </button>
                  <button
                    onClick={() => setActiveTab('users')}
                    className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition"
                  >
                    <div className="font-medium text-gray-900">User Management</div>
                    <div className="text-sm text-gray-500">View user accounts and activity</div>
                  </button>
                  <button
                    onClick={() => setActiveTab('analytics')}
                    className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition"
                  >
                    <div className="font-medium text-gray-900">Analytics</div>
                    <div className="text-sm text-gray-500">Revenue and performance metrics</div>
                  </button>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                🔧 System Status
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl text-green-600 mb-2">✅</div>
                  <div className="font-medium text-gray-900">Database</div>
                  <div className="text-sm text-green-600">Healthy</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl text-blue-600 mb-2">📧</div>
                  <div className="font-medium text-gray-900">Email Service</div>
                  <div className="text-sm text-blue-600">Active</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl text-purple-600 mb-2">💳</div>
                  <div className="font-medium text-gray-900">Payments</div>
                  <div className="text-sm text-purple-600">Processing</div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Other tabs will be implemented as separate components */}
        {activeTab !== 'overview' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-xl shadow-sm p-8 text-center"
          >
            <div className="text-6xl mb-4">🚧</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Management
            </h3>
            <p className="text-gray-600 mb-6">
              This section is under development. Advanced {activeTab} management features coming soon.
            </p>
            <div className="text-sm text-gray-500 italic">
              "Patience is the companion of wisdom. Great features are built with mindful intention."
            </div>
          </motion.div>
        )}

        {/* Dharma Message */}
        <div className="mt-12 text-center">
          <p className="text-gray-400 text-sm italic">
            "With great power comes great responsibility. Administer with wisdom and compassion."
          </p>
        </div>
      </div>
    </PageWrapper>
  );
}