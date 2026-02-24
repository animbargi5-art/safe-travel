import { Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";

import Layout from "./components/Layout";
import AuthDebug from "./components/AuthDebug";
import { BookingProvider } from "./context/BookingContext";
import { AuthProvider } from "./context/AuthContext";

import Home from "./pages/Home";
import FlightSearch from "./pages/FlightSearch";
import SmartFlightSearch from "./pages/SmartFlightSearch";
import EnhancedExperience from "./pages/EnhancedExperience";
import Flights from "./pages/Flights";
import Seats from "./pages/Seats";
import BookingSummary from "./pages/BookingSummary";
import Payment from "./pages/Payment";
import Confirmation from "./pages/Confirmation";
import Bookings from "./pages/Bookings";
import About from "./pages/About";
import Login from "./pages/Login";
import Register from "./pages/Register";
import AdminDashboard from "./pages/AdminDashboard";
import GroupBooking from "./pages/GroupBooking";
import GroupConfirmation from "./pages/GroupConfirmation";
import UserInsights from "./pages/UserInsights";
import UltraFastTest from "./pages/UltraFastTest";
import LiveMonitoring from "./pages/LiveMonitoring";
import NotFound from "./pages/NotFound";

export default function App() {
  const location = useLocation();

  return (
    <AuthProvider>
      <BookingProvider>
        <AuthDebug />
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route element={<Layout />}>
              <Route path="/" element={<Home />} />
              <Route path="/search" element={<FlightSearch />} />
              <Route path="/smart-search" element={<SmartFlightSearch />} />
              <Route path="/enhanced" element={<EnhancedExperience />} />
              <Route path="/flights" element={<Flights />} />
              <Route path="/seats/:flightId" element={<Seats />} />
              <Route path="/summary" element={<BookingSummary />} />
              <Route path="/payment" element={<Payment />} />
              <Route path="/confirmation" element={<Confirmation />} />
              <Route path="/bookings" element={<Bookings />} />
              <Route path="/insights" element={<UserInsights />} />
              <Route path="/ultra-fast-test" element={<UltraFastTest />} />
              <Route path="/live-monitoring" element={<LiveMonitoring />} />
              <Route path="/about" element={<About />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/group-booking/:flightId" element={<GroupBooking />} />
              <Route path="/group-confirmation" element={<GroupConfirmation />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </AnimatePresence>
      </BookingProvider>
    </AuthProvider>
  );
}
