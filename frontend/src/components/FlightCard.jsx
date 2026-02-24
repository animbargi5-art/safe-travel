import { motion } from "framer-motion";

export default function FlightCard({ flight, onSelect }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="card p-6 flex justify-between items-center"
    >
      {/* Flight Info */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-1">
          {flight.from_city} → {flight.to_city}
        </h3>

        <p className="text-sm text-muted">
          Departure: {flight.departure_time}
        </p>

        <p className="mt-1 text-blue-600 font-bold">
          ₹ {flight.price}
        </p>
      </div>

      {/* Action */}
      <button
        onClick={() => onSelect(flight.id)}
        className="btn-primary"
      >
        View Seats
      </button>
    </motion.div>
  );
}
