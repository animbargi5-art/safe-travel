export default function LoadingState({ message }) {
    return (
      <p className="text-center text-gray-500 animate-pulse">
        {message || "Loading…"}
      </p>
    );
  }
  