import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import api from '../services/api';

export default function BusinessIntelligenceDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
  }, [selectedPeriod]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/reporting/executive-dashboard?days=${selectedPeriod}`);
      setDashboardData(response.data.data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-4 text-gray-600">Loading business intelligence...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-800">{error}</p>
        <button 
          onClick={fetchDashboardData}
          className="mt-2 text-red-600 hover:text-red-800 underline"
        >
          Try Again
        </button>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'revenue', label: 'Revenue', icon: '💰' },
    { id: 'customers', label: 'Customers', icon: '👥' },
    { id: 'operations', label: 'Operations', icon: '⚙️' },
    { id: 'market', label: 'Market', icon: '🌍' }
  ];

  const periods = [
    { value: 7, label: '7 Days' },
    { value: 30, label: '30 Days' },
    { value: 90, label: '90 Days' },
    { value: 365, label: '1 Year' }
  ];

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Business Intelligence</h2>
          <p className="text-gray-600">Comprehensive analytics and insights</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            {periods.map(period => (
              <option key={period.value} value={period.value}>
                {period.label}
              </option>
            ))}
          </select>
          
          <button
            onClick={fetchDashboardData}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-white text-blue-600 shadow-sm'
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
        {activeTab === 'overview' && (
          <OverviewTab data={dashboardData} />
        )}
        
        {activeTab === 'revenue' && (
          <RevenueTab data={dashboardData} />
        )}
        
        {activeTab === 'customers' && (
          <CustomersTab data={dashboardData} />
        )}
        
        {activeTab === 'operations' && (
          <OperationsTab data={dashboardData} />
        )}
        
        {activeTab === 'market' && (
          <MarketTab data={dashboardData} />
        )}
      </motion.div>
    </div>
  );
}

function OverviewTab({ data }) {
  const { kpis, period } = data;

  return (
    <div className="space-y-6">
      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Revenue"
          value={kpis.total_revenue.formatted}
          growth={kpis.total_revenue.growth}
          icon="💰"
          color="green"
        />
        <KPICard
          title="Total Bookings"
          value={kpis.total_bookings.value.toLocaleString()}
          growth={kpis.total_bookings.growth}
          icon="✈️"
          color="blue"
        />
        <KPICard
          title="Avg Booking Value"
          value={kpis.average_booking_value.formatted}
          icon="📊"
          color="purple"
        />
        <KPICard
          title="Conversion Rate"
          value={kpis.conversion_rate.formatted}
          icon="🎯"
          color="orange"
        />
      </div>

      {/* Quick Stats */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Stats</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{kpis.new_customers.value}</div>
            <div className="text-sm text-gray-600">New Customers</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{kpis.total_bookings.total_attempts}</div>
            <div className="text-sm text-gray-600">Total Attempts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{period.days}</div>
            <div className="text-sm text-gray-600">Days Analyzed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {kpis.total_revenue.growth > 0 ? '📈' : kpis.total_revenue.growth < 0 ? '📉' : '➡️'}
            </div>
            <div className="text-sm text-gray-600">Trend</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function RevenueTab({ data }) {
  const { revenue_trends, kpis } = data;

  return (
    <div className="space-y-6">
      {/* Revenue Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Total Revenue</h3>
          <div className="text-3xl font-bold text-green-600">{kpis.total_revenue.formatted}</div>
          <div className={`text-sm ${kpis.total_revenue.growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {kpis.total_revenue.growth >= 0 ? '↗️' : '↘️'} {Math.abs(kpis.total_revenue.growth)}% vs previous period
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Average Transaction</h3>
          <div className="text-3xl font-bold text-blue-600">{kpis.average_booking_value.formatted}</div>
          <div className="text-sm text-gray-600">Per booking</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Growth Rate</h3>
          <div className={`text-3xl font-bold ${kpis.total_revenue.growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {kpis.total_revenue.growth >= 0 ? '+' : ''}{kpis.total_revenue.growth}%
          </div>
          <div className="text-sm text-gray-600">Revenue growth</div>
        </div>
      </div>

      {/* Daily Revenue Chart */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Daily Revenue Trend</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {revenue_trends.daily.slice(-14).map((day, index) => {
            const maxRevenue = Math.max(...revenue_trends.daily.map(d => d.revenue));
            const width = (day.revenue / maxRevenue) * 100;
            
            return (
              <div key={day.date} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 w-24">
                  {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
                <div className="flex-1 mx-4">
                  <div className="bg-gray-200 rounded-full h-4 relative">
                    <div 
                      className="bg-green-500 h-4 rounded-full transition-all duration-500"
                      style={{ width: `${width}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm font-medium text-gray-800 w-20 text-right">
                  ${day.revenue.toLocaleString()}
                </span>
                <span className="text-xs text-gray-500 w-16 text-right">
                  ({day.transactions} txn)
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Hourly Distribution */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Revenue by Hour</h3>
        <div className="grid grid-cols-6 md:grid-cols-12 gap-2">
          {revenue_trends.hourly.map((hour) => {
            const maxHourlyRevenue = Math.max(...revenue_trends.hourly.map(h => h.revenue));
            const height = (hour.revenue / maxHourlyRevenue) * 100;
            
            return (
              <div key={hour.hour} className="text-center">
                <div className="bg-gray-200 rounded h-16 flex items-end justify-center mb-1">
                  <div 
                    className="bg-blue-500 rounded w-full transition-all duration-500"
                    style={{ height: `${height}%` }}
                    title={`${hour.hour}:00 - $${hour.revenue.toLocaleString()}`}
                  />
                </div>
                <div className="text-xs text-gray-600">{hour.hour}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function CustomersTab({ data }) {
  const { customer_metrics } = data;

  return (
    <div className="space-y-6">
      {/* Customer Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">New Customers</h3>
          <div className="text-3xl font-bold text-blue-600">{customer_metrics.new_customers}</div>
          <div className="text-sm text-gray-600">This period</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Avg Lifetime Value</h3>
          <div className="text-3xl font-bold text-green-600">${customer_metrics.average_lifetime_value}</div>
          <div className="text-sm text-gray-600">Per customer</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Repeat Rate</h3>
          <div className="text-3xl font-bold text-purple-600">{customer_metrics.repeat_customer_rate}%</div>
          <div className="text-sm text-gray-600">Customer retention</div>
        </div>
      </div>

      {/* Customer Segments */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Customer Segments</h3>
        <div className="space-y-4">
          {customer_metrics.customer_segments.map((segment, index) => {
            const totalCustomers = customer_metrics.customer_segments.reduce((sum, s) => sum + s.count, 0);
            const percentage = (segment.count / totalCustomers) * 100;
            
            return (
              <div key={segment.segment} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${
                    segment.segment === 'High Value' ? 'bg-green-500' :
                    segment.segment === 'Medium Value' ? 'bg-blue-500' : 'bg-gray-500'
                  }`} />
                  <span className="font-medium text-gray-800">{segment.segment}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-800">{segment.count} customers</div>
                  <div className="text-sm text-gray-600">
                    ${segment.average_spent} avg • {percentage.toFixed(1)}%
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function OperationsTab({ data }) {
  const { operational_metrics } = data;

  return (
    <div className="space-y-6">
      {/* Operational Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Seat Utilization</h3>
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 mb-2">
              {operational_metrics.seat_utilization.rate}%
            </div>
            <div className="text-sm text-gray-600">
              {operational_metrics.seat_utilization.booked_seats} of {operational_metrics.seat_utilization.total_seats} seats
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Conversion Funnel</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Total Attempts</span>
              <span className="font-medium">{operational_metrics.booking_funnel.total_attempts}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Confirmed</span>
              <span className="font-medium text-green-600">{operational_metrics.booking_funnel.confirmed}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Conversion Rate</span>
              <span className="font-medium text-blue-600">{operational_metrics.booking_funnel.conversion_rate}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Routes */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Top Performing Routes</h3>
        <div className="space-y-3">
          {operational_metrics.top_routes.slice(0, 8).map((route, index) => (
            <div key={route.route} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                <span className="font-medium text-gray-800">{route.route}</span>
              </div>
              <div className="text-right">
                <div className="font-semibold text-green-600">${route.revenue.toLocaleString()}</div>
                <div className="text-sm text-gray-600">{route.bookings} bookings</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MarketTab({ data }) {
  const { market_insights } = data;

  return (
    <div className="space-y-6">
      {/* Price Analysis */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Price Analysis</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">${market_insights.price_analysis.min_price}</div>
            <div className="text-sm text-gray-600">Minimum</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">${market_insights.price_analysis.average_price}</div>
            <div className="text-sm text-gray-600">Average</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">${market_insights.price_analysis.median_price}</div>
            <div className="text-sm text-gray-600">Median</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">${market_insights.price_analysis.max_price}</div>
            <div className="text-sm text-gray-600">Maximum</div>
          </div>
        </div>
      </div>

      {/* Popular Destinations */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Popular Destinations</h3>
        <div className="space-y-3">
          {market_insights.popular_destinations.slice(0, 6).map((destination, index) => (
            <div key={destination.city} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                <span className="font-medium text-gray-800">{destination.city}</span>
              </div>
              <div className="text-right">
                <div className="font-semibold text-blue-600">{destination.bookings} bookings</div>
                <div className="text-sm text-gray-600">${destination.average_price} avg</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Seasonal Trends */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Seasonal Trends</h3>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
          {market_insights.seasonal_trends.map((month) => {
            const maxRevenue = Math.max(...market_insights.seasonal_trends.map(m => m.revenue));
            const height = (month.revenue / maxRevenue) * 100;
            
            return (
              <div key={month.month} className="text-center">
                <div className="bg-gray-200 rounded h-20 flex items-end justify-center mb-2">
                  <div 
                    className="bg-green-500 rounded w-full transition-all duration-500"
                    style={{ height: `${height}%` }}
                    title={`${month.month_name} - $${month.revenue.toLocaleString()}`}
                  />
                </div>
                <div className="text-xs text-gray-600">{month.month_name}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function KPICard({ title, value, growth, icon, color }) {
  const colorClasses = {
    green: 'bg-green-50 border-green-200',
    blue: 'bg-blue-50 border-blue-200',
    purple: 'bg-purple-50 border-purple-200',
    orange: 'bg-orange-50 border-orange-200'
  };

  return (
    <div className={`rounded-lg border p-6 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-4">
        <span className="text-2xl">{icon}</span>
        {growth !== undefined && (
          <span className={`text-sm font-medium ${
            growth >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {growth >= 0 ? '↗️' : '↘️'} {Math.abs(growth)}%
          </span>
        )}
      </div>
      <div className="text-2xl font-bold text-gray-800 mb-1">{value}</div>
      <div className="text-sm font-medium text-gray-600">{title}</div>
    </div>
  );
}