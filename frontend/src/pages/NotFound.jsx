import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import PageWrapper from "../components/PageWrapper";
import SectionTitle from "../components/ui/SectionTitle";

export default function NotFound() {
  return (
    <PageWrapper>
      <SectionTitle
  title="Available Flights"
  subtitle="Choose a journey that suits your path"
/>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="min-h-[70vh] flex items-center justify-center"
      >
        <div className="text-center bg-white p-12 rounded-2xl shadow-sm hover:shadow-md transition max-w-md w-full">
          
          {/* Error Code */}
          <h1 className="text-6xl font-bold text-blue-700 mb-4">
            404
          </h1>

          {/* Message */}
          <p className="text-gray-600 mb-8 text-lg">
            The page you’re looking for does not exist.
          </p>

          {/* Action */}
          <Link
            to="/"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition"
          >
            Go Home
          </Link>

          {/* Calm note */}
          <p className="mt-8 text-xs text-gray-400 italic">
            When the path is unclear, return to the beginning.
          </p>
        </div>
      </motion.div>
    </PageWrapper>
  );
}
