import PageWrapper from "../components/PageWrapper";
import SectionTitle from "../components/ui/SectionTitle";
import UltraFastBookingTest from "../components/UltraFastBookingTest";
import NanosecondBookingTest from "../components/NanosecondBookingTest";

export default function UltraFastTest() {
  return (
    <PageWrapper>
      <SectionTitle
        title="⚡ Ultra-Fast & Nanosecond Booking Performance"
        subtitle="Test lightning-speed booking and true nanosecond-level operations"
      />
      
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Nanosecond Engine - Top Priority */}
        <NanosecondBookingTest />
        
        {/* Ultra-Fast Engine - Secondary */}
        <UltraFastBookingTest />
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Performance Highlights */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200">
            <div className="text-3xl mb-2">🚀</div>
            <h3 className="font-bold text-purple-800 mb-2">Nanosecond Engine</h3>
            <p className="text-purple-700 text-sm">
              True nanosecond performance with pure in-memory operations and atomic thread-safe booking
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl">
            <div className="text-3xl mb-2">⚡</div>
            <h3 className="font-bold text-blue-800 mb-2">Ultra-Fast Booking</h3>
            <p className="text-blue-700 text-sm">
              Microsecond-level seat booking with optimized database operations and instant cache updates
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl">
            <div className="text-3xl mb-2">🎯</div>
            <h3 className="font-bold text-green-800 mb-2">Instant Allocation</h3>
            <p className="text-green-700 text-sm">
              Railway-style waitlist processing with nanosecond allocation when seats become available
            </p>
          </div>
        </div>
        
        <div className="mt-8 bg-gray-50 p-6 rounded-xl">
          <h3 className="font-bold text-gray-800 mb-4">🔧 Technical Optimizations</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Backend Optimizations:</h4>
              <ul className="space-y-1 text-gray-600">
                <li>• Thread-safe seat locking mechanism</li>
                <li>• Atomic database operations</li>
                <li>• Connection pooling with 20+ connections</li>
                <li>• Prepared statement caching</li>
                <li>• Background task processing</li>
                <li>• In-memory caching for hot data</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Database Optimizations:</h4>
              <ul className="space-y-1 text-gray-600">
                <li>• SQLite WAL mode for concurrent access</li>
                <li>• Optimized indexes on booking queries</li>
                <li>• Single-query seat availability checks</li>
                <li>• Batch operations for bulk updates</li>
                <li>• Memory-mapped I/O for faster access</li>
                <li>• Query performance monitoring</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </PageWrapper>
  );
}