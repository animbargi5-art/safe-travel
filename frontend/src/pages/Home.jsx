import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import PageWrapper from "../components/PageWrapper";
import SectionTitle from "../components/ui/SectionTitle";

export default function Home() {
  const navigate = useNavigate();

  return (
    <PageWrapper>
      <SectionTitle
  title="Available Flights"
  subtitle="Choose a journey that suits your path"
/>

      <motion.div
        initial={{ opacity: 0, y: 32 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="min-h-[70vh] flex items-center justify-center"
      >
        <div className="bg-white rounded-2xl shadow-sm hover:shadow-md transition p-12 text-center max-w-md w-full">
          
          {/* Title */}
          <h1 className="text-4xl font-bold text-blue-700 mb-4">
            Safe Travel ✈️
          </h1>

          {/* Subtitle */}
          <p className="text-gray-600 mb-8 leading-relaxed">
            Journey with harmony, order, and dharma.
            <br />
            Every seat, every moment — aligned perfectly.
          </p>

          {/* Primary Action */}
          <button
            onClick={() => navigate("/search")}
            className="px-8 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition shadow-md"
          >
            Search Flights
          </button>

          {/* Calm Quote */}
          <p className="mt-8 text-xs text-gray-400 italic">
            “Order sustains the universe.”
          </p>
        </div>
      </motion.div>
    </PageWrapper>
  );
}
