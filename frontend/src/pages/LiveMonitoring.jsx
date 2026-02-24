import PageWrapper from "../components/PageWrapper";
import SectionTitle from "../components/ui/SectionTitle";
import LiveDashboard from "../components/LiveDashboard";
import { useAuth } from "../context/AuthContext";

export default function LiveMonitoring() {
  const { user } = useAuth();
  const isAdmin = user?.email === 'test@safetravelapp.com';

  return (
    <PageWrapper>
      <SectionTitle
        title={isAdmin ? "🔍 Live Admin Dashboard" : "📊 Live System Monitor"}
        subtitle={
          isAdmin 
            ? "Real-time backend performance, booking speeds, and system activity monitoring"
            : "Live system status and your booking activity"
        }
      />
      
      <div className="max-w-7xl mx-auto">
        <LiveDashboard />
        
        {/* Information Panel */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-200">
          <h3 className="font-bold text-gray-800 mb-4">
            {isAdmin ? "🔧 Admin Dashboard Features" : "📱 Live Monitoring Features"}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">
                {isAdmin ? "System Monitoring:" : "What You Can See:"}
              </h4>
              <ul className="space-y-1 text-gray-600 text-sm">
                {isAdmin ? (
                  <>
                    <li>• Real-time booking performance metrics</li>
                    <li>• Nanosecond-level timing precision</li>
                    <li>• Live user activity tracking</li>
                    <li>• System throughput and success rates</li>
                    <li>• Waitlist allocation monitoring</li>
                    <li>• Performance testing capabilities</li>
                  </>
                ) : (
                  <>
                    <li>• System health and status</li>
                    <li>• Booking system performance</li>
                    <li>• Your recent activity</li>
                    <li>• Live connection status</li>
                  </>
                )}
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">
                {isAdmin ? "Performance Insights:" : "System Features:"}
              </h4>
              <ul className="space-y-1 text-gray-600 text-sm">
                {isAdmin ? (
                  <>
                    <li>• Nanosecond booking engine status</li>
                    <li>• Real-time throughput calculations</li>
                    <li>• Memory structure monitoring</li>
                    <li>• Active user session tracking</li>
                    <li>• Performance test execution</li>
                    <li>• Live activity stream</li>
                  </>
                ) : (
                  <>
                    <li>• Ultra-fast booking system</li>
                    <li>• Railway-style waitlist allocation</li>
                    <li>• Real-time seat availability</li>
                    <li>• Instant booking confirmation</li>
                  </>
                )}
              </ul>
            </div>
          </div>
          
          {isAdmin && (
            <div className="mt-4 p-4 bg-purple-100 rounded-lg border border-purple-200">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-purple-600">🚀</span>
                <span className="font-semibold text-purple-800">Admin Controls</span>
              </div>
              <p className="text-purple-700 text-sm">
                Use the "Run Test" button to execute live performance tests and see real-time 
                nanosecond booking speeds. All activities are logged and displayed in the live stream.
              </p>
            </div>
          )}
        </div>
      </div>
    </PageWrapper>
  );
}