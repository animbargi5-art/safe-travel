import { motion } from "framer-motion";

/**
 * PageWrapper
 * - Consistent spacing
 * - Smooth page transitions
 * - Centralized animation logic
 */
export default function PageWrapper({ children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
      className="max-w-6xl mx-auto px-6 py-6"
    >
      {children}
    </motion.div>
  );
}
