import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function IPLookup() {
  const [ipAddress, setIpAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleLookup = async () => {
    if (!ipAddress.trim()) {
      setError('Please enter an IP address');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.get(`${API_URL}/api/identify/${ipAddress}?skip_cache=false`);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to lookup IP address');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleLookup();
    }
  };

  return (
    <div className="space-y-6" data-testid="ip-lookup">
      {/* Search Box */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">IP Address Lookup</h2>
        <p className="text-gray-600 mb-6">
          Enter an IP address to identify the company using our multi-layer identification system.
        </p>
        
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="e.g., 8.8.8.8"
            value={ipAddress}
            onChange={(e) => setIpAddress(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            data-testid="ip-input"
          />
          <button
            onClick={handleLookup}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
            data-testid="lookup-button"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Looking up...</span>
              </>
            ) : (
              <span>Lookup</span>
            )}
          </button>
        </div>

        {/* Example IPs */}
        <div className="mt-4 flex flex-wrap gap-2">
          <span className="text-sm text-gray-600">Try examples:</span>
          {['8.8.8.8', '17.172.224.1', '52.34.12.56', '1.1.1.1'].map(ip => (
            <button
              key={ip}
              onClick={() => setIpAddress(ip)}
              className="text-sm px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
            >
              {ip}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center space-x-3">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <div className="font-semibold text-red-900">Error</div>
              <div className="text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Main Result */}
          <div className="card bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-sm font-medium text-gray-600 mb-1">Company Identified</div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {result.company_name || 'Unknown'}
                </div>
                {result.is_isp && (
                  <span className="badge badge-warning">Internet Service Provider</span>
                )}
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-600 mb-1">Confidence</div>
                <div className="text-3xl font-bold text-blue-600">
                  {Math.round(result.confidence * 100)}%
                </div>
              </div>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Basic Info */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
              <div className="space-y-3">
                <InfoRow label="IP Address" value={result.ip_address} />
                <InfoRow label="Identification Method" value={result.method} />
                <InfoRow label="Cached Result" value={result.cached ? 'Yes' : 'No'} />
                {result.hostname && <InfoRow label="Reverse DNS" value={result.hostname} />}
              </div>
            </div>

            {/* Location Info */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Location</h3>
              <div className="space-y-3">
                {result.city && <InfoRow label="City" value={result.city} />}
                {result.region && <InfoRow label="Region" value={result.region} />}
                {result.country && <InfoRow label="Country" value={result.country} />}
                {result.asn && <InfoRow label="ASN" value={result.asn} />}
                {result.asn_org && <InfoRow label="ASN Organization" value={result.asn_org} />}
              </div>
            </div>
          </div>

          {/* All Layer Results */}
          {result.all_results && result.all_results.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">All Identification Layers</h3>
              <div className="space-y-3">
                {result.all_results.map((layer, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-bold text-blue-600">
                        {index + 1}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{layer.company_name || 'No result'}</div>
                        <div className="text-sm text-gray-600">Method: {layer.method}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-gray-700">
                        {Math.round(layer.confidence * 100)}%
                      </div>
                      {layer.is_isp && (
                        <span className="text-xs text-orange-600">ISP</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
      <span className="text-sm font-medium text-gray-600">{label}</span>
      <span className="text-sm text-gray-900 font-mono">{value}</span>
    </div>
  );
}

export default IPLookup;