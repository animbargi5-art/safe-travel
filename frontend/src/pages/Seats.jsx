import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import PageWrapper from "../components/PageWrapper";
import api from "../services/api";
import SectionTitle from "../components/ui/SectionTitle";
import AutoSeatAllocation from "../components/AutoSeatAllocation";
import MLRecommendations from "../components/MLRecommendations";
import { useBooking } from "../context/BookingContext";
import { useAuth } from "../context/AuthContext";

export default function Seats() {
  const { flightId } = useParams();
  const navigate = useNavigate();
  const { bookingData, updateBookingData } = useBooking();
  const { user, isAuthenticated } = useAuth();

  const [seats, setSeats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeat, setSelectedSeat] = useState(null);
  const [holdingSeats, setHoldingSeats] = useState(false);
  const [allocationOptions, setAllocationOptions] = useState(null);
  const [showManualSelection, setShowManualSelection] = useState(false);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      console.log('User not authenticated, redirecting to login...');
      navigate('/login');
      return;
    }
  }, [isAuthenticated, loading, navigate]);

  // 🔹 Fetch seats and allocation options
  useEffect(() => {
    if (!isAuthenticated || loading) return;

    const fetchData = async () => {
      try {
        console.log(`Fetching seats for flight ${flightId}...`);
        const [seatsResponse, optionsResponse] = await Promise.all([
          api.get(`/seats/available/${flightId}`),
          api.get(`/booking/allocation-options/${flightId}`)
        ]);
        
        console.log('Seats data received:', seatsResponse.data.length, 'seats');
        console.log('Allocation options received:', Object.keys(optionsResponse.data));
        
        setSeats(seatsResponse.data);
        setAllocationOptions(optionsResponse.data);
      } catch (err) {
        console.error("Error fetching data:", err);
        if (err.response?.status === 401) {
          console.log('Authentication error, redirecting to login...');
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [flightId, isAuthenticated, loading, navigate]);

  // 🔹 Manual seat selection
  const handleSeatClick = async (seat) => {
    if (seat.status !== "AVAILABLE" || holdingSeats) return;

    setHoldingSeats(true);
    try {
      const response = await api.post('/booking/hold', {
        flight_id: parseInt(flightId),
        seat_id: seat.id
      });

      updateSeatsAndSelection(seat, response.data);

    } catch (error) {
      console.error("Error holding seat:", error);
      alert("Could not hold seat. Please try again.");
    } finally {
      setHoldingSeats(false);
    }
  };

  // 🔹 Auto seat allocation
  const handleAutoAllocate = async (preference = "ANY", seatClass = "ECONOMY", strategy = "BEST_AVAILABLE") => {
    setHoldingSeats(true);
    try {
      const response = await api.post('/booking/auto-allocate', {
        flight_id: parseInt(flightId),
        seat_class_preference: seatClass,
        position_preference: preference,
        strategy: strategy
      });

      const allocatedSeat = response.data.seat;
      updateSeatsAndSelection(allocatedSeat, response.data.booking);

      // Show success message
      alert(`✈️ Perfect! Auto-allocated seat ${allocatedSeat.seat_number}!\n\n${response.data.allocation_reason}`);

    } catch (error) {
      console.error("Error auto-allocating seat:", error);
      alert("Could not auto-allocate seat. Please try manual selection.");
    } finally {
      setHoldingSeats(false);
    }
  };

  // Helper function to update seats and selection
  const updateSeatsAndSelection = (seat, booking) => {
    // Update local state
    setSeats(prev => 
      prev.map(s => 
        s.id === seat.id 
          ? { ...s, status: "HOLD" }
          : s.status === "HOLD"
          ? { ...s, status: "AVAILABLE" } // Clear other holds
          : s
      )
    );

    setSelectedSeat(seat);
    
    // Store booking data
    updateBookingData({
      seat: seat,
      booking: booking
    });
  };

  const handleProceed = () => {
    if (!selectedSeat) {
      alert("Please select a seat first");
      return;
    }
    navigate("/summary");
  };

  if (loading) {
    return (
      <PageWrapper>
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">
              {!isAuthenticated ? "Checking authentication..." : "Loading seat options..."}
            </p>
          </div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <SectionTitle
        title="Select Your Seat"
        subtitle="Let wisdom guide your choice, or choose with intention"
      />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="min-h-[70vh] max-w-6xl mx-auto"
      >
        {/* Auto-allocation section */}
        <div className="mb-8">
          <AutoSeatAllocation
            allocationOptions={allocationOptions}
            onAutoAllocate={handleAutoAllocate}
            isLoading={holdingSeats}
          />
        </div>

        {/* ML Seat Recommendations */}
        <MLRecommendations type="seats" flightId={flightId} />

        {/* Manual selection toggle */}
        <div className="text-center mb-6">
          <button
            onClick={() => setShowManualSelection(!showManualSelection)}
            className="text-gray-600 hover:text-gray-800 font-medium flex items-center gap-2 mx-auto"
          >
            {showManualSelection ? '▼' : '▶'} Or choose manually from seat map
          </button>
        </div>

        {/* Manual seat selection */}
        {showManualSelection && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white rounded-xl p-6 shadow-sm"
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-6 text-center">
              ✋ Manual Seat Selection
            </h3>

            {/* Legend */}
            <div className="flex justify-center gap-6 mb-8 text-sm">
              <Legend color="green" label="Available" />
              <Legend color="yellow" label="Selected" />
              <Legend color="red" label="Unavailable" />
            </div>

            {/* Seat Layout */}
            {seats.length === 0 ? (
              <p className="text-center text-gray-500">
                No seats available for this flight
              </p>
            ) : (
              <div className="flex flex-col gap-3 items-center max-w-md mx-auto">
                {/* Group seats by row */}
                {[...new Set(seats.map((s) => s.row))].sort((a, b) => a - b).map((row) => (
                  <div key={row} className="flex items-center gap-2">
                    
                    {/* Row number */}
                    <div className="w-8 text-right text-sm text-gray-400 mr-2">
                      {row}
                    </div>

                    {seats
                      .filter((seat) => seat.row === row)
                      .sort((a, b) => a.col.localeCompare(b.col))
                      .map((seat, index) => {
                        const isSelected = selectedSeat?.id === seat.id;
                        const isAvailable = seat.status === "AVAILABLE";
                        const isHeld = seat.status === "HOLD";
                        
                        let colorClass = "bg-red-300 cursor-not-allowed"; // Unavailable
                        if (isAvailable) colorClass = "bg-green-200 hover:bg-green-300 cursor-pointer";
                        if (isHeld || isSelected) colorClass = "bg-yellow-200";

                        return (
                          <div key={seat.id} className="flex items-center">
                            <button
                              disabled={!isAvailable || holdingSeats}
                              onClick={() => handleSeatClick(seat)}
                              className={`${colorClass} 
                                w-10 h-10 
                                rounded-lg 
                                text-xs font-medium
                                text-gray-800 
                                transition-all duration-200
                                hover:scale-105 
                                hover:shadow-md 
                                disabled:opacity-50
                                ${isSelected ? 'ring-2 ring-blue-500' : ''}
                                ${holdingSeats ? 'opacity-50' : ''}`}
                              title={`Seat ${seat.seat_number || `${row}${seat.col}`} - ${seat.seat_class}`}
                            >
                              {seat.col}
                            </button>

                            {/* ✈️ Aisle after C */}
                            {seat.col === "C" && (
                              <div className="w-6 flex justify-center">
                                <div className="w-px h-6 bg-gray-300"></div>
                              </div>
                            )}
                          </div>
                        );
                      })}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Selected seat info */}
        {selectedSeat && (
          <div className="mt-8 text-center">
            <div className="bg-green-50 rounded-xl p-6 max-w-md mx-auto border border-green-200">
              <div className="text-2xl mb-2">✅</div>
              <p className="text-green-800 font-semibold text-lg">
                Seat {selectedSeat.seat_number || `${selectedSeat.row}${selectedSeat.col}`} Selected
              </p>
              <p className="text-green-700 text-sm mt-1">
                {selectedSeat.seat_class} Class • Row {selectedSeat.row}
              </p>
              <p className="text-green-600 text-xs mt-2">
                Held for 10 minutes while you complete booking
              </p>
            </div>
          </div>
        )}

        {/* Action */}
        <div className="mt-10 flex flex-col items-center gap-4">
          <button
            onClick={handleProceed}
            disabled={!selectedSeat || holdingSeats}
            className="px-8 py-4 bg-blue-600 text-white rounded-xl shadow-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-lg font-medium"
          >
            {holdingSeats ? "Processing..." : "Continue to Booking Summary"}
          </button>

          <p className="text-center text-sm text-gray-500 max-w-md">
            Your dharma-aligned journey continues with the perfect seat selection.
          </p>
        </div>
      </motion.div>
    </PageWrapper>
  );
}

/* 🔹 Legend component */
function Legend({ color, label }) {
  const colorMap = {
    green: "bg-green-200",
    yellow: "bg-yellow-200", 
    red: "bg-red-300"
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`w-4 h-4 ${colorMap[color]} rounded`}></div>
      <span className="text-sm text-gray-600">{label}</span>
    </div>
  );
}