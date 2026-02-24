import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import LoadingState from './ui/LoadingState';
import Card from './ui/Card';

const MLRecommendations = ({ type = 'flights', flightId = null, limit = 5 }) => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) return;
    
    fetchRecommendations();
  }, [user, type, flightId]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);

      let response;
      if (type === 'flights') {
        response = await api.get(`/ml/recommendations/flights?limit=${limit}`);
        setRecommendations(response.data.recommendations);
      } else if (type === 'seats' && flightId) {
        response = await api.get(`/ml/recommendations/seats/${flightId}`);
        setRecommendations(response.data.recommendations);
      }
    } catch (err) {
      console.error('Error fetching ML recommendations:', err);
      setError('Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;
  if (loading) return <LoadingState message="Getting personalized recommendations..." />;
  if (error) return <div className="text-red-600 text-center py-4">{error}</div>;
  if (!recommendations.length) return null;

  return (
    <Card className="mb-6">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🤖 AI Recommendations for You
        </h3>
        
        {type === 'flights' && (
          <div className="space-y-4">
            {recommendations.map((rec, index) => (
              <div key={rec.id} className="border-l-4 border-blue-500 pl-4 py-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {rec.from_city} → {rec.to_city}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {new Date(rec.departure_time).toLocaleDateString()} at{' '}
                      {new Date(rec.departure_time).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                    <p className="text-sm text-blue-600 font-medium">
                      ₹{rec.price.toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-green-600">
                      {Math.round(rec.score)}% match
                    </div>
                  </div>
                </div>
                <div className="mt-2">
                  <div className="flex flex-wrap gap-1">
                    {rec.reasons.map((reason, idx) => (
                      <span
                        key={idx}
                        className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                      >
                        {reason}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {type === 'seats' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((rec, index) => (
              <div key={rec.seat_id} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-medium text-gray-900">
                      Seat {rec.seat_number}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {rec.seat_class} • Row {rec.row}
                    </p>
                  </div>
                  <div className="text-sm font-medium text-green-600">
                    {Math.round(rec.score)}% match
                  </div>
                </div>
                <div className="flex flex-wrap gap-1">
                  {rec.reasons.map((reason, idx) => (
                    <span
                      key={idx}
                      className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded"
                    >
                      {reason}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-4 text-xs text-gray-500 text-center">
          Recommendations based on your booking history and preferences
        </div>
      </div>
    </Card>
  );
};

export default MLRecommendations;