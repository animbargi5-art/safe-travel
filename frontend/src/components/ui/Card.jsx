export default function Card({ children }) {
    return (
      <div className="bg-white rounded-2xl shadow-sm hover:shadow-md transition p-6">
        {children}
      </div>
    );
  }
  