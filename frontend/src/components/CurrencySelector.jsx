import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';

export default function CurrencySelector({ 
  selectedCurrency = 'USD', 
  onCurrencyChange, 
  region = 'US',
  className = '' 
}) {
  const [currencies, setCurrencies] = useState([]);
  const [popularCurrencies, setPopularCurrencies] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [exchangeRates, setExchangeRates] = useState({});

  useEffect(() => {
    fetchCurrencies();
    fetchPopularCurrencies();
    fetchExchangeRates();
  }, [region]);

  const fetchCurrencies = async () => {
    try {
      const response = await api.get('/currency/supported');
      setCurrencies(response.data);
    } catch (error) {
      console.error('Failed to fetch currencies:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPopularCurrencies = async () => {
    try {
      const response = await api.get(`/currency/popular/${region}`);
      setPopularCurrencies(response.data.currencies);
    } catch (error) {
      console.error('Failed to fetch popular currencies:', error);
    }
  };

  const fetchExchangeRates = async () => {
    try {
      // Fetch rates for popular currencies
      const rates = {};
      const popularCodes = ['USD', 'EUR', 'GBP', 'INR', 'JPY'];
      
      for (const currency of popularCodes) {
        if (currency !== selectedCurrency) {
          const response = await api.get(`/currency/exchange-rate/${selectedCurrency}/${currency}`);
          rates[currency] = response.data.exchange_rate;
        }
      }
      
      setExchangeRates(rates);
    } catch (error) {
      console.error('Failed to fetch exchange rates:', error);
    }
  };

  const handleCurrencySelect = (currency) => {
    onCurrencyChange(currency);
    setIsOpen(false);
    fetchExchangeRates(); // Update rates for new base currency
  };

  const selectedCurrencyInfo = currencies.find(c => c.code === selectedCurrency);

  if (loading) {
    return (
      <div className={`animate-pulse bg-gray-200 rounded-lg h-10 w-24 ${className}`}></div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {/* Currency Selector Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:border-blue-500 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <span className="text-lg">{selectedCurrencyInfo?.symbol || '$'}</span>
        <span className="font-medium">{selectedCurrency}</span>
        <svg 
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Currency Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 mt-2 w-80 bg-white border border-gray-200 rounded-xl shadow-lg z-50 max-h-96 overflow-y-auto"
          >
            {/* Popular Currencies */}
            {popularCurrencies.length > 0 && (
              <div className="p-4 border-b border-gray-100">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  🌟 Popular in {region}
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {popularCurrencies.map((currency) => (
                    <button
                      key={currency.code}
                      onClick={() => handleCurrencySelect(currency.code)}
                      className={`flex items-center gap-2 p-2 rounded-lg text-left hover:bg-blue-50 transition-colors ${
                        selectedCurrency === currency.code ? 'bg-blue-100 border border-blue-300' : ''
                      }`}
                    >
                      <span className="text-lg">{currency.symbol}</span>
                      <div>
                        <div className="font-medium text-sm">{currency.code}</div>
                        {exchangeRates[currency.code] && (
                          <div className="text-xs text-gray-500">
                            1 {selectedCurrency} = {exchangeRates[currency.code].toFixed(4)}
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* All Currencies */}
            <div className="p-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                💱 All Currencies
              </h3>
              <div className="space-y-1">
                {currencies.map((currency) => (
                  <button
                    key={currency.code}
                    onClick={() => handleCurrencySelect(currency.code)}
                    className={`flex items-center justify-between w-full p-3 rounded-lg text-left hover:bg-gray-50 transition-colors ${
                      selectedCurrency === currency.code ? 'bg-blue-50 border border-blue-200' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg w-8">{currency.symbol}</span>
                      <div>
                        <div className="font-medium">{currency.code}</div>
                        <div className="text-sm text-gray-500">{currency.name}</div>
                      </div>
                    </div>
                    
                    {exchangeRates[currency.code] && (
                      <div className="text-sm text-gray-500">
                        {exchangeRates[currency.code].toFixed(4)}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Exchange Rate Info */}
            <div className="p-4 bg-gray-50 border-t border-gray-100">
              <div className="text-xs text-gray-600 text-center">
                💡 Exchange rates update every 15 minutes
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Click outside to close */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        ></div>
      )}
    </div>
  );
}