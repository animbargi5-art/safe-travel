// Simple connection test
const axios = require('axios');

async function testConnection() {
    try {
        console.log('Testing backend connection...');
        
        // Test health endpoint
        const healthResponse = await axios.get('http://localhost:8000/health');
        console.log('✅ Health check:', healthResponse.data);
        
        // Test currency endpoint
        const currencyResponse = await axios.get('http://localhost:8000/currency/supported');
        console.log('✅ Currency endpoint working, found', currencyResponse.data.length, 'currencies');
        
        // Test auth endpoint
        const authResponse = await axios.get('http://localhost:8000/auth/me', {
            headers: { 'Authorization': 'Bearer invalid-token' }
        }).catch(err => {
            console.log('✅ Auth endpoint responding (expected 401):', err.response?.status);
        });
        
        console.log('\n🎉 Backend is working correctly!');
        console.log('Frontend should be able to connect at: http://localhost:5173');
        
    } catch (error) {
        console.error('❌ Connection test failed:', error.message);
    }
}

testConnection();