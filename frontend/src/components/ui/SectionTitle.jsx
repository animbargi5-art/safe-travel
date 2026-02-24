export default function SectionTitle({ title, subtitle }) {
  return (
    <div className="text-center mb-10">
      <h1 className="text-3xl font-bold text-blue-700">
        {title}
      </h1>

      {subtitle && (
        <p className="text-gray-500 mt-2">
          {subtitle}
        </p>
      )}
    </div>
  );
}
