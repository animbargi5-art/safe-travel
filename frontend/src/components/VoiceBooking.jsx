import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function VoiceBooking({ onSearchResult, className = '' }) {
  const { user } = useAuth();
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [supportedCommands, setSupportedCommands] = useState(null);
  
  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    // Check if browser supports speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setError(null);
      };
      
      recognitionRef.current.onresult = (event) => {
        const current = event.resultIndex;
        const transcript = event.results[current][0].transcript;
        setTranscript(transcript);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
        if (transcript) {
          processVoiceCommand(transcript);
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        setIsListening(false);
        setError(`Speech recognition error: ${event.error}`);
      };
    }

    // Fetch supported commands
    fetchSupportedCommands();
  }, []);

  const fetchSupportedCommands = async () => {
    try {
      const response = await api.get('/voice-booking/supported-commands');
      setSupportedCommands(response.data);
    } catch (error) {
      console.error('Failed to fetch supported commands:', error);
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      setResponse(null);
      setError(null);
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const processVoiceCommand = async (text) => {
    if (!text.trim()) return;

    setIsProcessing(true);
    try {
      const response = await api.post('/voice-booking/process-text', {
        text: text,
        language: 'en'
      });

      setResponse(response.data);
      
      // If it's a search command, trigger search
      if (response.data.success && response.data.action === 'search_flights' && onSearchResult) {
        onSearchResult(response.data.parameters);
      }
      
    } catch (error) {
      console.error('Voice command processing failed:', error);
      setError('Failed to process voice command. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTextInput = (e) => {
    if (e.key === 'Enter') {
      processVoiceCommand(e.target.value);
      e.target.value = '';
    }
  };

  const testVoiceCommand = async (command) => {
    setTranscript(command);
    await processVoiceCommand(command);
  };

  if (!user) {
    return (
      <div className={`text-center p-6 bg-gray-50 rounded-lg ${className}`}>
        <p className="text-gray-600">Please log in to use voice booking</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6 rounded-t-xl text-white">
        <h3 className="text-xl font-bold mb-2">🎤 Voice Booking Assistant</h3>
        <p className="text-purple-100">
          Speak naturally to search and book flights
        </p>
      </div>

      <div className="p-6">
        {/* Voice Input Section */}
        <div className="text-center mb-6">
          <div className="relative inline-block">
            <motion.button
              onClick={isListening ? stopListening : startListening}
              disabled={isProcessing}
              className={`w-20 h-20 rounded-full flex items-center justify-center text-white font-bold text-2xl transition-all duration-300 ${
                isListening 
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                  : 'bg-blue-500 hover:bg-blue-600'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isListening ? '🛑' : '🎤'}
            </motion.button>
            
            {isListening && (
              <motion.div
                className="absolute inset-0 rounded-full border-4 border-red-300"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1 }}
              />
            )}
          </div>
          
          <p className="mt-3 text-sm text-gray-600">
            {isListening ? 'Listening... Speak now!' : 'Click to start voice command'}
          </p>
          
          {isProcessing && (
            <div className="mt-2 flex items-center justify-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              <span className="text-sm text-gray-600">Processing...</span>
            </div>
          )}
        </div>

        {/* Text Input Alternative */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Or type your command:
          </label>
          <input
            type="text"
            placeholder="Try: 'Find flights from Mumbai to Delhi tomorrow'"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={handleTextInput}
            disabled={isProcessing}
          />
        </div>

        {/* Current Transcript */}
        {transcript && (
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-700">
              <strong>You said:</strong> "{transcript}"
            </p>
          </div>
        )}

        {/* Response */}
        <AnimatePresence>
          {response && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`mb-4 p-4 rounded-lg ${
                response.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
              }`}
            >
              <div className="flex items-start">
                <span className="text-2xl mr-3">
                  {response.success ? '✅' : '❌'}
                </span>
                <div className="flex-1">
                  <p className={`font-medium ${response.success ? 'text-green-800' : 'text-red-800'}`}>
                    {response.message}
                  </p>
                  
                  {response.parameters && (
                    <div className="mt-2 text-sm text-gray-600">
                      <strong>Detected:</strong>
                      {response.parameters.from_city && ` From: ${response.parameters.from_city}`}
                      {response.parameters.to_city && ` To: ${response.parameters.to_city}`}
                      {response.parameters.departure_date && ` Date: ${response.parameters.departure_date}`}
                      {response.parameters.class && ` Class: ${response.parameters.class}`}
                      {response.parameters.passengers && ` Passengers: ${response.parameters.passengers}`}
                    </div>
                  )}
                  
                  {response.suggestions && (
                    <div className="mt-3">
                      <p className="text-sm font-medium text-gray-700 mb-2">Try these commands:</p>
                      <div className="space-y-1">
                        {response.suggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => testVoiceCommand(suggestion)}
                            className="block w-full text-left text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-2 py-1 rounded"
                          >
                            "{suggestion}"
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-2 text-xs text-gray-500">
                    Confidence: {(response.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Example Commands */}
        {supportedCommands && (
          <div className="border-t pt-4">
            <h4 className="font-semibold text-gray-800 mb-3">💡 Example Commands</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(supportedCommands.commands).map(([type, info]) => (
                <div key={type} className="bg-gray-50 p-3 rounded-lg">
                  <h5 className="font-medium text-gray-800 capitalize mb-2">{type}</h5>
                  <div className="space-y-1">
                    {info.examples.slice(0, 2).map((example, index) => (
                      <button
                        key={index}
                        onClick={() => testVoiceCommand(example)}
                        className="block w-full text-left text-sm text-gray-600 hover:text-blue-600 hover:bg-white px-2 py-1 rounded transition-colors"
                      >
                        "{example}"
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Voice Tips */}
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h5 className="font-medium text-yellow-800 mb-2">🎯 Voice Tips</h5>
          <ul className="text-sm text-yellow-700 space-y-1">
            <li>• Speak clearly and at a normal pace</li>
            <li>• Use full city names (Mumbai, not Bombay)</li>
            <li>• Include specific dates when possible</li>
            <li>• Mention number of passengers if more than one</li>
          </ul>
        </div>
      </div>
    </div>
  );
}