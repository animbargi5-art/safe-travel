import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import PageWrapper from '../components/PageWrapper';
import SectionTitle from '../components/ui/SectionTitle';
import { useAuth } from '../context/AuthContext';

export default function BIDemo() {
  const { isAuthenticated } = useAuth();
  const [demoData, setDemoData] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState('revenue');

  useEffect(() => {
    // Generate demo data
    setDemoData(generateDemoData());
  }, []);

  const generateDemoData = () => {
    return {
      kpis: {
        total_revenue: { value: 125000, growth: 15.3, formatted: '$125,000' },
        total_bookings: { value: 342, growth: 8.7 },
        conversion_rate: { value: 73.2, formatted: '73.2%' },
        avg_booking_value: { value: 365, formatted: '$365' }
      },
      trends: {
        daily: Array.from({ length: 14 }, (_, i) => ({
          date: new Date(Date.now() - (13 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          revenue: 8000 + Math.random() * 4000,
          bookings: 20 + Math.random() * 15
        })),
        hourly: Array.from({ length: 24 }, (_, i) => ({
          hour: i,
          revenue: 200 + Math.random() * 800,
          bookings: 1 + Math.random() * 5
        }))
      },
      segments: [
        { name: 'High Value', count: 45, avg_spent: 850, color: 'green' },
        { name: 'Medium Value', count: 128, avg_spent: 420, color: 'blue' },
        { name: 'Low Value', count: 169, avg_spent: 180, color: 'gray' }
      ],
      routes: [
        { route: 'NYC → LAX', bookings: 89, revenue: 32450 },
        { route: 'SFO → NYC', bookings: 76, revenue: 28900 },
        { route: 'CHI → MIA', bookings: 65, revenue: 24300 },
        { route: 'LAX → SEA', bookings: 54, revenue: 19800 }
      ]
    };
  };

  if (!isAuthenticated) {
    return (
      <PageWrapper>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Authentication Required</h2>
          <p className="text-gray-600">Please log in to see Business Intelligence demo.</p>
        </div>
      </PageWrapper>
    );
  }

  if (!demoData) {
    return (
      <PageWrapper>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading BI demo...</span>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <SectionTitle
        title="Business Intelligence Demo"
        subtitle="Experience advanced analytics and data-driven insights"
      />

      <div className="space-y-8">
        {/* KPI Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6"
        >
          <KPICard
            title="Total Revenue"
            value={demoData.kpis.total_revenue.formatted}
            growth={demoData.kpis.total_revenue.growth}
            icon="💰"
            color="green"
          />
          <KPICard
            title="Total Bookings"
            value={demoData.kpis.total_bookings.value.toLocaleString()}
            growth={demoData.kpis.total_bookings.growth}
            icon="✈️"
            color="blue"
          />
          <KPICard
            title="Conversion Rate"
            value={demoData.kpis.conversion_rate.formatted}
            icon="🎯"
            color="purple"
          />
          <KPICard
            title="Avg Booking Value"
            value={demoData.kpis.avg_booking_value.formatted}
            icon="📊"
            color="orange"
          />
        </motion.div>

        {/* Interactive Charts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-sm p-6"
        >
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-800">Revenue Trends</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => setSelectedMetric('revenue')}
                className={`px-3 py-1 rounded text-sm ${
                  selectedMetric === 'revenue' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                Revenue
              </button>
              <button
                onClick={() => setSelectedMetric('bookings')}
                className={`px-3 py-1 rounded text-sm ${
                  selectedMetric === 'bookings' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                Bookings
              </button>
            </div>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto">
            {demoData.trends.daily.map((day, index) => {
              const maxValue = Math.max(...demoData.trends.daily.map(d => 
                selectedMetric === 'revenue' ? d.revenue : d.bookings
              ));
              const value = selectedMetric === 'revenue' ? day.revenue : day.bookings;
              const width = (value / maxValue) * 100;
              
              return (
                <div key={day.date} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 w-24">
                    {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </span>
                  <div className="flex-1 mx-4">
                    <div className="bg-gray-200 rounded-full h-4 relative">
                      <div 
                        className={`h-4 rounded-full transition-all duration-500 ${
                          selectedMetric === 'revenue' ? 'bg-green-500' : 'bg-blue-500'
                        }`}
                        style={{ width: `${width}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-sm font-medium text-gray-800 w-20 text-right">
                    {selectedMetric === 'revenue' 
                      ? `$${Math.round(value).toLocaleString()}` 
                      : Math.round(value)
                    }
                  </span>
                </div>
              );
            })}
          </div>
        </motion.div>

        {/* Customer Segments & Top Routes */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-lg shadow-sm p-6"
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Customer Segments</h3>
            <div className="space-y-4">
              {demoData.segments.map((segment) => {
                const totalCustomers = demoData.segments.reduce((sum, s) => sum + s.count, 0);
                const percentage = (segment.count / totalCustomers) * 100;
                
                return (
                  <div key={segment.name} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full ${
                        segment.color === 'green' ? 'bg-green-500' :
                        segment.color === 'blue' ? 'bg-blue-500' : 'bg-gray-500'
                      }`} />
                      <span className="font-medium text-gray-800">{segment.name}</span>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-gray-800">{segment.count} customers</div>
                      <div className="text-sm text-gray-600">
                        ${segment.avg_spent} avg • {percentage.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg shadow-sm p-6"
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Top Routes</h3>
            <div className="space-y-3">
              {demoData.routes.map((route, index) => (
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
          </motion.div>
        </div>

        {/* Insights & Recommendations */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">💡 Key Insights</h3>
            <div className="space-y-3">
              <InsightItem
                text="Revenue growth of 15.3% indicates strong market performance"
                type="positive"
              />
              <InsightItem
                text="Peak booking hours are 10 AM - 2 PM for optimal staffing"
                type="operational"
              />
              <InsightItem
                text="High-value customers represent 13% but generate 35% of revenue"
                type="customer"
              />
              <InsightItem
                text="NYC-LAX route shows highest profitability per seat"
                type="market"
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">🎯 AI Recommendations</h3>
            <div className="space-y-3">
              <RecommendationItem
                text="Implement dynamic pricing during peak hours (10 AM - 2 PM)"
                priority="high"
              />
              <RecommendationItem
                text="Launch loyalty program targeting medium-value customers"
                priority="medium"
              />
              <RecommendationItem
                text="Increase capacity on NYC-LAX route by 20%"
                priority="high"
              />
              <RecommendationItem
                text="Optimize marketing spend on high-conversion channels"
                priority="medium"
              />
            </div>
          </div>
        </motion.div>

        {/* Demo Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-blue-50 border border-blue-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold text-blue-800 mb-4">🚀 Business Intelligence Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-700">
            <div>
              <h4 className="font-medium mb-2">Analytics Capabilities:</h4>
              <ul className="space-y-1">
                <li>• Real-time KPI monitoring and tracking</li>
                <li>• Revenue forecasting and trend analysis</li>
                <li>• Customer segmentation and lifetime value</li>
                <li>• Operational efficiency metrics</li>
                <li>• Market insights and competitive analysis</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Advanced Features:</h4>
              <ul className="space-y-1">
                <li>• AI-powered recommendations and insights</li>
                <li>• Interactive data visualization</li>
                <li>• Multi-period comparative analysis</li>
                <li>• Export capabilities for external analysis</li>
                <li>• Predictive analytics and forecasting</li>
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
            "In the wisdom of data lies the path to mindful business growth. 
            Let insights guide decisions with compassion for both profit and purpose."
          </p>
          <p className="text-green-600 text-sm mt-2">
            - Safe Travel Business Intelligence Philosophy
          </p>
        </motion.div>
      </div>
    </PageWrapper>
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

function InsightItem({ text, type }) {
  const typeColors = {
    positive: 'bg-green-100 text-green-800',
    operational: 'bg-blue-100 text-blue-800',
    customer: 'bg-purple-100 text-purple-800',
    market: 'bg-orange-100 text-orange-800'
  };

  return (
    <div className="flex items-start space-x-3">
      <span className={`text-xs px-2 py-1 rounded-full font-medium ${typeColors[type]}`}>
        {type}
      </span>
      <p className="text-sm text-gray-700 flex-1">{text}</p>
    </div>
  );
}

function RecommendationItem({ text, priority }) {
  const priorityColors = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-gray-100 text-gray-800'
  };

  return (
    <div className="flex items-start space-x-3">
      <span className={`text-xs px-2 py-1 rounded-full font-medium ${priorityColors[priority]}`}>
        {priority}
      </span>
      <p className="text-sm text-gray-700 flex-1">{text}</p>
    </div>
  );
}