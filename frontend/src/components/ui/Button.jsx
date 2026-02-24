export default function Button({ children, onClick, variant = "primary" }) {
    const base = "px-6 py-3 rounded-xl font-medium transition";
  
    const variants = {
      primary: "bg-blue-600 text-white hover:bg-blue-700",
      secondary: "border border-gray-300 text-gray-700 hover:bg-gray-50",
    };
  
    return (
      <button onClick={onClick} className={`${base} ${variants[variant]}`}>
        {children}
      </button>
    );
  }
  