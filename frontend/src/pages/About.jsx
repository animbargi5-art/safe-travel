import { motion } from "framer-motion";
import PageWrapper from "../components/PageWrapper";

import SectionTitle from "../components/ui/SectionTitle";

export default function About() {
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
        <div className="max-w-3xl w-full bg-white rounded-2xl p-10 shadow-sm hover:shadow-md transition">
          
          {/* Title */}
          <h2 className="text-3xl font-bold text-blue-700 mb-6 text-center">
            Our Guiding Values
          </h2>

          {/* Divider */}
          <div className="w-16 h-1 bg-blue-200 mx-auto mb-6 rounded-full" />

          {/* Content */}
          <p className="text-gray-600 leading-relaxed text-lg text-center">
            This platform is inspired by the timeless principle of
            <span className="font-medium text-gray-800"> dharma </span>
            — that every action has its proper time, place, and order.
            <br /><br />
            We aim to provide a travel experience that is
            <span className="font-medium"> calm</span>,
            <span className="font-medium"> transparent</span>, and
            <span className="font-medium"> respectful</span>,
            allowing you to move with confidence and clarity.
          </p>

          {/* Quote / Krishna alignment */}
          <div className="mt-8 p-4 bg-blue-50 rounded-xl text-center">
            <p className="text-blue-800 italic">
              “Yogaḥ karmasu kauśalam” — Excellence in action is yoga.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Bhagavad Gītā 2.50
            </p>
          </div>
        </div>
      </motion.div>
    </PageWrapper>
  );
}
