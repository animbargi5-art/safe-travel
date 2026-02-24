import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import PageWrapper from '../components/PageWrapper';
import SectionTitle from '../components/ui/SectionTitle';
import PaymentAnalytics from '../components/PaymentAnalytics';
import { useAuth } from '../context/AuthContext';

export default function PaymentDashboard() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

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
        title="Payment Dashboard"
        subtitle="Advanced analytics and security insights for your payments"
      />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="space-y-8"
      >
        {/* Enhanced Payment Analytics */}
        <PaymentAnalytics />

        {/* Security Notice */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <span className="text-2xl">🛡️</span>
            <div>
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                Enhanced Security Features
              </h3>
              <div className="text-green-700 space-y-2">
                <p>Your payments are protected by our advanced security system:</p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Real-time fraud detection and risk scoring</li>
                  <li>Payment velocity monitoring and rate limiting</li>
                  <li>Suspicious pattern detection and alerts</li>
                  <li>Secure webhook processing with signature verification</li>
                  <li>Comprehensive audit logging and analytics</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Dharma Message */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <span className="text-3xl mb-3 block">🧘</span>
          <p className="text-blue-800 italic">
            "In the flow of mindful transactions, security and trust create the foundation for peaceful journeys."
          </p>
          <p className="text-blue-600 text-sm mt-2">
            - Safe Travel Philosophy
          </p>
        </div>
      </motion.div>
    </PageWrapper>
  );
}