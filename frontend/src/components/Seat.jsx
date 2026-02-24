/**
 * Seat component
 * - Stateless & reusable
 * - Status-driven UI
 * - Calm, clear interaction
 */

export default function Seat({ seat, onSelect }) {
  const isBooked = seat.status === "CONFIRMED";
  const isHold = seat.status === "HOLD";
  const isAvailable = seat.status === "AVAILABLE";
  const [selectedSeatId, setSelectedSeatId] = useState(null);

  const handleSeatClick = (seatId) => {
    setSelectedSeatId(seatId);
  };

  const isSelected = selectedSeatId === seat.id;

  let seatClasses =
    "w-10 h-10 rounded-lg text-xs font-semibold transition duration-300 flex items-center justify-center";

  if (isBooked) {
    seatClasses += " bg-red-300 text-gray-700 cursor-not-allowed";
  } else if (isHold) {
    seatClasses += " bg-yellow-200 text-gray-800 cursor-not-allowed";
  } else if (isAvailable) {
    seatClasses +=
      " bg-green-200 text-gray-800 hover:scale-110 hover:shadow-md";
  }

  return (
    <button
      disabled={!isAvailable}
      onClick={() => onSelect(seat.id)}
      className={seatClasses}
      aria-label={`Seat ${seat.row}${seat.col}`}
      title={`Seat ${seat.row}${seat.col}`}
    >
      {seat.col}
    </button>
  );
}
