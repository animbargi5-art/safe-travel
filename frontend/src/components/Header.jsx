import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import { useState } from "react";

export default function Header() {
  const { user, logout, isAuthenticated, loading } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
  };

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="w-full bg-white border-b border-gray-200 sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        
        {/* Logo / Brand */}
        <NavLink
          to="/"
          className="text-xl font-bold text-blue-700 hover:text-blue-800 transition"
        >
          Safe Travel ✈️
        </NavLink>

        {/* Navigation */}
        <nav className="flex items-center gap-6 text-sm font-medium">
          <NavLink
            to="/search"
            className={({ isActive }) =>
              isActive
                ? "text-blue-700"
                : "text-gray-600 hover:text-blue-600 transition"
            }
          >
            Search
          </NavLink>

          <NavLink
            to="/smart-search"
            className={({ isActive }) =>
              isActive
                ? "text-blue-700"
                : "text-gray-600 hover:text-blue-600 transition"
            }
          >
            🤖 Smart Search
          </NavLink>

          <NavLink
            to="/enhanced"
            className={({ isActive }) =>
              isActive
                ? "text-blue-700"
                : "text-gray-600 hover:text-blue-600 transition"
            }
          >
            🚀 Enhanced
          </NavLink>

          <NavLink
            to="/flights"
            className={({ isActive }) =>
              isActive
                ? "text-blue-700"
                : "text-gray-600 hover:text-blue-600 transition"
            }
          >
            Flights
          </NavLink>

          {isAuthenticated && (
            <NavLink
              to="/bookings"
              className={({ isActive }) =>
                isActive
                  ? "text-blue-700"
                  : "text-gray-600 hover:text-blue-600 transition"
              }
            >
              My Bookings
            </NavLink>
          )}

          <NavLink
            to="/about"
            className={({ isActive }) =>
              isActive
                ? "text-blue-700"
                : "text-gray-600 hover:text-blue-600 transition"
            }
          >
            About
          </NavLink>

          {/* Auth Section */}
          {loading ? (
            // Show loading state while checking authentication
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gray-200 rounded-full animate-pulse"></div>
              <div className="w-16 h-4 bg-gray-200 rounded animate-pulse"></div>
            </div>
          ) : isAuthenticated ? (
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition"
              >
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-700">
                    {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                  </span>
                </div>
                <span className="hidden md:inline">{user?.full_name || user?.username}</span>
                <span className="text-xs">▼</span>
              </button>

              {/* User Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-800">{user?.full_name}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                  </div>
                  
                  <NavLink
                    to="/bookings"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setShowUserMenu(false)}
                  >
                    My Bookings
                  </NavLink>
                  
                  <NavLink
                    to="/insights"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setShowUserMenu(false)}
                  >
                    🤖 Travel Insights
                  </NavLink>
                  
                  <NavLink
                    to="/live-monitoring"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setShowUserMenu(false)}
                  >
                    {user?.email === 'test@safetravelapp.com' ? '🔍 Live Admin Dashboard' : '📊 Live System Status'}
                  </NavLink>
                  
                  <NavLink
                    to="/ultra-fast-test"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setShowUserMenu(false)}
                  >
                    ⚡ Performance Test
                  </NavLink>
                  
                  <NavLink
                    to="/admin"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setShowUserMenu(false)}
                  >
                    🛠️ Admin Dashboard
                  </NavLink>
                  
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <NavLink
                to="/login"
                className="text-gray-600 hover:text-blue-600 transition"
              >
                Sign In
              </NavLink>
              <NavLink
                to="/register"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Sign Up
              </NavLink>
            </div>
          )}
        </nav>
      </div>

      {/* Click outside to close menu */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </motion.header>
  );
}
