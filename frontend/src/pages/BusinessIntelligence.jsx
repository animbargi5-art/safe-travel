import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import PageWrapper from '../components/PageWrapper';
import SectionTitle from '../components/ui/SectionTitle';
import BusinessIntelligenceDashboard from '../components/BusinessIntelligenceDashboard';
import { useAuth } from '../context/AuthContext';

export default function BusinessIntelligence() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <PageWrapper>
      <SectionTitle
        title="Business Intelligence"
        subtitle="Advanced analytics and insights for data-driven decisions"
      />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="space-y-8"
      >
        {/* Welcome Message */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start space-x-4">
            <span className="text-3xl">📊</span>
            <div>
              <h3 className="text-lg font-semibold text-blue-800 mb-2">
                Welcome to Business Intelligence, {user?.full_name || 'Admin'}
              </h3>
              <p className="text-blue-700">
                Gain deep insights into your flight booking business with comprehensive analytics, 
                real-time metrics, and predictive insights. Make data-driven decisions to optimize 
                performance and drive growth.
              </p>
            </div>
          </div>
        </div>

        {/* Main Dashboard */}
        <BusinessIntelligenceDashboard />

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <QuickActionCard
              title="Export Revenue Report"
              description="Download detailed revenue analysis"
              icon="📈"
              action="export-revenue"
            />
            <QuickActionCard
              title="Customer Analytics"
              description="Deep dive into customer behavior"
              icon="👥"
              action="customer-analytics"
            />
            <QuickActionCard
              title="Predictive Insights"
              description="AI-powered forecasts and trends"
              icon="🔮"
              action="predictive-insights"
            />
            <QuickActionCard
              title="Market Analysis"
              description="Competitive and market insights"
              icon="🌍"
              action="market-analysis"
            />
          </div>
        </div>

        {/* Key Insights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">💡 Key Insights</h3>
            <div className="space-y-3">
              <InsightItem
                text="Peak booking hours are between 9 AM - 11 AM and 2 PM - 4 PM"
                type="operational"
              />
              <InsightItem
                text="Weekend bookings show 23% higher average transaction value"
                type="revenue"
              />
              <InsightItem
                text="Customer retention rate has improved by 15% this quarter"
                type="customer"
              />
              <InsightItem
                text="NYC → LAX route generates highest revenue per seat"
                type="market"
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">🎯 Recommendations</h3>
            <div className="space-y-3">
              <RecommendationItem
                text="Consider dynamic pricing during peak hours to maximize revenue"
                priority="high"
              />
              <RecommendationItem
                text="Implement weekend promotion campaigns to boost bookings"
                priority="medium"
              />
              <RecommendationItem
                text="Expand capacity on high-performing routes"
                priority="high"
              />
              <RecommendationItem
                text="Develop loyalty program to improve customer retention"
                priority="medium"
              />
            </div>
          </div>
        </div>

        {/* Dharma Message */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <span className="text-3xl mb-3 block">🧘</span>
          <p className="text-green-800 italic">
            "In the wisdom of data lies the path to mindful business growth. 
            Let insights guide decisions with compassion for both profit and purpose."
          </p>
          <p className="text-green-600 text-sm mt-2">
            - Safe Travel Business Philosophy
          </p>
        </div>
      </motion.div>
    </PageWrapper>
  );
}

function QuickActionCard({ title, description, icon, action }) {
  const handleAction = async () => {
    switch (action) {
      case 'export-revenue':
        // Trigger revenue report export
        try {
          const response = await fetch('/api/reporting/export/csv?report_type=revenue&days=30');
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'revenue_report.csv';
          a.click();
        } catch (error) {
          console.error('Export failed:', error);
        }
        break;
      case 'customer-analytics':
        // Navigate to customer analytics
        console.log('Navigate to customer analytics');
        break;
      case 'predictive-insights':
        // Show predictive insights
        console.log('Show predictive insights');
        break;
      case 'market-analysis':
        // Show market analysis
        console.log('Show market analysis');
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  return (
    <button
      onClick={handleAction}
      className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition"
    >
      <div className="flex items-center space-x-3 mb-2">
        <span className="text-2xl">{icon}</span>
        <h4 className="font-medium text-gray-800">{title}</h4>
      </div>
      <p className="text-sm text-gray-600">{description}</p>
    </button>
  );
}

function InsightItem({ text, type }) {
  const typeColors = {
    operational: 'bg-blue-100 text-blue-800',
    revenue: 'bg-green-100 text-green-800',
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