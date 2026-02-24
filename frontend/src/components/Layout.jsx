import { Outlet } from "react-router-dom";
import Header from "./Header";

export default function Layout() {
  return (
    <div className="bg-calm transition-colors duration-500">
      
      {/* Global Header */}
      <Header />

      {/* Main Page Content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Optional Footer (future-ready) */}
      <footer className="py-6 text-center text-sm text-gray-400">
        © {new Date().getFullYear()} Safe Travel · Order brings peace
      </footer>
    </div>
  );
}
