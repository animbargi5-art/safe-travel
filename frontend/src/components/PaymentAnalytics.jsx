import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import api from '../services/api';

export default function PaymentAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [userAnalytics, setUserAnalytics] = useState(null);
  const [fraudData, setFraudData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      
      // Fetch different types of analytics
      const [analyticsRes, userRes, fraudRes] = await Promise.allSettled([
        api.get('/payment/analytics?days=30'),
        api.get('/payment/my-analytics'),
        api.get('/payment/fraud-detection?days=7')
      ]);

      if (analyticsRes.status === 'fulfilled') {
        setAnalytics(analyticsRes.value.data);
      }
      
      if (userRes.status === 'fulfilled') {
        setUserAnalytics(userRes.value.data);
      }
      
      if (fraudRes.status === 'fulfilled') {
        setFraudData(fraudRes.value.data);
      }

    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Failed to load payment analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        <span className="ml-2 text-gray-600">Loading analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button 
          onClick={fetchAnalytics}
          className="mt-2 text-red-600 hover:text-red-800 underline"
        >
          Try Again
        </button>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'personal', label: 'My Payments', icon: '👤' },
    { id: 'security', label: 'Security', icon: '🔒' }
  ];

  return (
    <div className="bg-white rounded-2xl shadow-sm p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Payment Analytics</h2>
        <p className="text-gray-600">Insights into payment patterns and security</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 rounded-lg p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition ${
              activeTab === tab.id
                ? 'bg-white text-green-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === 'overview' && analytics && (
          <OverviewTab analytics={analytics} />
        )}
        
        {activeTab === 'personal' && userAnalytics && (
          <PersonalTab userAnalytics={userAnalytics} />
        )}
        
        {activeTab === 'security' && fraudData && (
          <SecurityTab fraudData={fraudData} />
        )}
      </motion.div>
    </div>
  );
}

function OverviewTab({ analytics }) {
  const { revenue_summary, daily_revenue, top_routes, refund_analysis } = analytics;

  return (
    <div className="space-y-6">
      {/* Revenue Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Revenue"
          value={`$${revenue_summary.total_revenue.toLocaleString()}`}
          subtitle={`${revenue_summary.period_days} days`}
          icon="💰"
          color="green"
        />
        <MetricCard
          title="Transactions"
          value={revenue_summary.transaction_count.toLocaleString()}
          subtitle={`${revenue_summary.success_rate}% success rate`}
          icon="📈"
          color="blue"
        />
        <MetricCard
          title="Avg Transaction"
          value={`$${revenue_summary.average_transaction_value}`}
          subtitle="Per booking"
          icon="💳"
          color="purple"
        />
        <MetricCard
          title="Refunds"
          value={`$${revenue_summary.refunded_amount.toLocaleString()}`}
          subtitle={`${revenue_summary.failed_payments} failed`}
          icon="↩️"
          color="orange"
        />
      </div>

      {/* Daily Revenue Chart */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Daily Revenue Trend</h3>
        <div className="space-y-2">
          {daily_revenue.slice(0, 7).map((day, index) => (
            <div key={day.date} className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{day.date}</span>
              <div className="flex items-center space-x-2">
                <div 
                  className="bg-green-200 h-2 rounded"
                  style={{ width: `${(day.revenue / Math.max(...daily_revenue.map(d => d.revenue))) * 100}px` }}
                ></div>
                <span className="text-sm font-medium">${day.revenue.toLocaleString()}</span>
                <span className="text-xs text-gray-500">({day.transactions} txn)</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Routes */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Top Routes by Revenue</h3>
        <div className="space-y-3">
          {top_routes.slice(0, 5).map((route, index) => (
            <div key={route.route} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                <span className="font-medium text-gray-800">{route.route}</span>
              </div>
              <div className="text-right">
                <div className="font-semibold text-green-600">${route.revenue.toLocaleString()}</div>
                <div className="text-xs text-gray-500">{route.bookings} bookings</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PersonalTab({ userAnalytics }) {
  const { payment_stats, velocity_check } = userAnalytics;

  return (
    <div className="space-y-6">
      {/* Personal Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Total Spent"
          value={`$${payment_stats.total_spent.toLocaleString()}`}
          subtitle="All time"
          icon="💸"
          color="green"
        />
        <MetricCard
          title="Payments Made"
          value={payment_stats.payment_count}
          subtitle="Successful transactions"
          icon="✅"
          color="blue"
        />
        <MetricCard
          title="Average Payment"
          value={`$${payment_stats.average_payment}`}
          subtitle="Per transaction"
          icon="📊"
          color="purple"
        />
      </div>

      {/* Payment Velocity */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Payment Activity</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(velocity_check).map(([period, data]) => (
            <div key={period} className="text-center">
              <div className="text-2xl font-bold text-gray-800">{data.payment_count}</div>
              <div className="text-sm text-gray-600 capitalize">{period.replace('_', ' ')}</div>
              <div className="text-xs text-gray-500">${data.total_amount.toLocaleString()}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Payment History Timeline */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Payment Timeline</h3>
        <div className="space-y-2">
          {payment_stats.first_payment_date && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">First Payment:</span>
              <span className="font-medium">{new Date(payment_stats.first_payment_date).toLocaleDateString()}</span>
            </div>
          )}
          {payment_stats.last_payment_date && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Last Payment:</span>
              <span className="font-medium">{new Date(payment_stats.last_payment_date).toLocaleDateString()}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SecurityTab({ fraudData }) {
  const { anomalies, total_anomalies, high_risk_count, medium_risk_count } = fraudData;

  return (
    <div className="space-y-6">
      {/* Security Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Total Anomalies"
          value={total_anomalies}
          subtitle="Last 7 days"
          icon="🚨"
          color="red"
        />
        <MetricCard
          title="High Risk"
          value={high_risk_count}
          subtitle="Requires attention"
          icon="⚠️"
          color="orange"
        />
        <MetricCard
          title="Medium Risk"
          value={medium_risk_count}
          subtitle="Under review"
          icon="🔍"
          color="yellow"
        />
      </div>

      {/* Anomaly List */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Security Events</h3>
        {anomalies.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <span className="text-4xl mb-2 block">🛡️</span>
            <p>No security anomalies detected</p>
            <p className="text-sm">Your payments are secure</p>
          </div>
        ) : (
          <div className="space-y-3">
            {anomalies.slice(0, 10).map((anomaly, index) => (
              <div key={index} className="bg-white rounded-lg p-3 border-l-4 border-red-400">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium text-gray-800 capitalize">
                      {anomaly.type.replace('_', ' ')}
                    </div>
                    <div className="text-sm text-gray-600">{anomaly.description}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      User: {anomaly.user_email}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-bold ${
                      anomaly.risk_score >= 80 ? 'text-red-600' :
                      anomaly.risk_score >= 50 ? 'text-orange-600' : 'text-yellow-600'
                    }`}>
                      Risk: {anomaly.risk_score}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ title, value, subtitle, icon, color }) {
  const colorClasses = {
    green: 'bg-green-50 border-green-200 text-green-800',
    blue: 'bg-blue-50 border-blue-200 text-blue-800',
    purple: 'bg-purple-50 border-purple-200 text-purple-800',
    orange: 'bg-orange-50 border-orange-200 text-orange-800',
    red: 'bg-red-50 border-red-200 text-red-800',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800'
  };

  return (
    <div className={`rounded-lg border p-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
      </div>
      <div className="text-2xl font-bold mb-1">{value}</div>
      <div className="text-sm font-medium">{title}</div>
      <div className="text-xs opacity-75">{subtitle}</div>
    </div>
  );
}