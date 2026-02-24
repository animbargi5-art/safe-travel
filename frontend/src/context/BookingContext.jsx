import { createContext, useContext, useState } from 'react';

const BookingContext = createContext();

export const useBooking = () => {
  const context = useContext(BookingContext);
  if (!context) {
    throw new Error('useBooking must be used within a BookingProvider');
  }
  return context;
};

export const BookingProvider = ({ children }) => {
  const [bookingData, setBookingData] = useState({
    flight: null,
    seat: null,
    booking: null,
    passenger: {
      name: '',
      email: '',
      phone: ''
    }
  });

  const updateBookingData = (data) => {
    setBookingData(prev => ({ ...prev, ...data }));
  };

  const clearBookingData = () => {
    setBookingData({
      flight: null,
      seat: null,
      booking: null,
      passenger: {
        name: '',
        email: '',
        phone: ''
      }
    });
  };

  return (
    <BookingContext.Provider value={{
      bookingData,
      updateBookingData,
      clearBookingData
    }}>
      {children}
    </BookingContext.Provider>
  );
};