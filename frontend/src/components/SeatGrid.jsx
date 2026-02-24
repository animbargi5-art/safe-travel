import Seat from "./Seat";

/**
 * SeatGrid
 * - Pure layout component
 * - Uses Seat as atomic unit
 * - Backend-driven seat data
 */
export default function SeatGrid({ seats, onSeatSelect }) {
  if (!seats || seats.length === 0) {
    return (
      <p className="text-center text-gray-500">
        No seats available
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-3 items-center">
      {[...new Set(seats.map((s) => s.row))].map((row) => (
        <div key={row} className="flex items-center gap-2">
          
          {/* Row number */}
          <div className="w-8 text-right text-sm text-gray-400 mr-2">
            {row}
          </div>

          {seats
            .filter((seat) => seat.row === row)
            .map((seat) => (
              <div key={seat.id} className="flex items-center">
                <Seat
                  seat={seat}
                  onSelect={onSeatSelect}
                />

                {/* ✈️ Aisle gap after C */}
                {seat.col === "C" && (
                  <div className="w-6"></div>
                )}
              </div>
            ))}
        </div>
      ))}
    </div>
  );
}
