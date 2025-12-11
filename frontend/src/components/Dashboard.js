import React from 'react';

function Dashboard({ analytics, stats }) {
  if (!analytics) {
    return <div>Loading...</div>;
  }

  const { 
    total_visitors, 
    identified_visitors, 
    identification_rate,
    top_companies,
    visitors_by_country,
    recent_visitors 
  } = analytics;

  return (
    <div className="space-y-6" data-testid="dashboard">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stat-card">
          <div className="metric-value">{total_visitors}</div>
          <div className="metric-label">Total Visitors (7 days)</div>
        </div>
        <div className="stat-card">
          <div className="metric-value">{identified_visitors}</div>
          <div className="metric-label">Companies Identified</div>
        </div>
        <div className="stat-card">
          <div className="metric-value">{identification_rate}%</div>
          <div className="metric-label">Identification Rate</div>
        </div>
        <div className="stat-card">
          <div className="metric-value">{stats?.cache_stats?.total_cached_ips || 0}</div>
          <div className="metric-label">Cached IPs</div>
        </div>
      </div>

      {/* System Status */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <StatusBadge label="WHOIS" active={true} />
          <StatusBadge label="Reverse DNS" active={true} />
          <StatusBadge label="ASN Lookup" active={true} />
          <StatusBadge label="IPinfo.io" active={stats?.layers_available?.ipinfo || false} />
          <StatusBadge label="ipapi.co" active={true} />
          <StatusBadge label="ip-api.com" active={true} />
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Companies */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Companies (7 days)</h2>
          {top_companies && top_companies.length > 0 ? (
            <div className="space-y-3">
              {top_companies.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{item.company}</div>
                    <div className="text-xs text-gray-500">Confidence: {item.avg_confidence}%</div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-blue-600">{item.count}</div>
                    <div className="text-xs text-gray-500">visits</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No data available</p>
          )}
        </div>

        {/* Visitors by Country */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Visitors by Country</h2>
          {visitors_by_country && visitors_by_country.length > 0 ? (
            <div className="space-y-3">
              {visitors_by_country.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium text-blue-600">
                      {item.country?.substring(0, 2) || '??'}
                    </div>
                    <div className="font-medium text-gray-900">{item.country || 'Unknown'}</div>
                  </div>
                  <div className="text-lg font-semibold text-gray-700">{item.count}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No data available</p>
          )}
        </div>
      </div>

      {/* Recent Visitors */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Visitors</h2>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>IP Address</th>
                <th>Location</th>
                <th>Confidence</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {recent_visitors && recent_visitors.slice(0, 10).map((visitor) => (
                <tr key={visitor.id || visitor._id}>
                  <td>
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">
                        {visitor.company_name || 'Unknown'}
                      </span>
                      {visitor.is_isp && (
                        <span className="badge badge-warning">ISP</span>
                      )}
                    </div>
                  </td>
                  <td className="font-mono text-gray-600">{visitor.ip_address}</td>
                  <td className="text-gray-600">
                    {visitor.city && visitor.country ? `${visitor.city}, ${visitor.country}` : visitor.country || 'N/A'}
                  </td>
                  <td>
                    <ConfidenceBar score={visitor.confidence_score} />
                  </td>
                  <td className="text-gray-500 text-xs">
                    {new Date(visitor.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ label, active }) {
  return (
    <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${
      active ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
    }`}>
      <div className={`w-2 h-2 rounded-full ${
        active ? 'bg-green-500' : 'bg-gray-400'
      }`}></div>
      <span className={`text-sm font-medium ${
        active ? 'text-green-700' : 'text-gray-500'
      }`}>{label}</span>
    </div>
  );
}

function ConfidenceBar({ score }) {
  const percentage = Math.round(score * 100);
  const color = percentage >= 80 ? 'bg-green-500' : percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500';
  
  return (
    <div className="w-24">
      <div className="confidence-bar">
        <div 
          className={`confidence-fill ${color}`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      <div className="text-xs text-gray-500 mt-1">{percentage}%</div>
    </div>
  );
}

export default Dashboard;