import React from 'react';

function Analytics({ analytics }) {
  if (!analytics) {
    return <div>Loading analytics...</div>;
  }

  const { top_companies, visitors_by_country, identification_rate } = analytics;

  return (
    <div className="space-y-6" data-testid="analytics">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="stat-card">
          <div className="metric-value">{identification_rate}%</div>
          <div className="metric-label">Identification Success Rate</div>
          <div className="mt-2 text-xs text-gray-600">
            Target: 70-80% accuracy
          </div>
        </div>
        <div className="stat-card">
          <div className="metric-value">{top_companies?.length || 0}</div>
          <div className="metric-label">Unique Companies</div>
          <div className="mt-2 text-xs text-gray-600">
            Last 7 days
          </div>
        </div>
        <div className="stat-card">
          <div className="metric-value">{visitors_by_country?.length || 0}</div>
          <div className="metric-label">Countries</div>
          <div className="mt-2 text-xs text-gray-600">
            Global reach
          </div>
        </div>
      </div>

      {/* Identification Methods Breakdown */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Identification Layer Performance</h2>
        <div className="space-y-4">
          <LayerPerformance 
            name="Layer 1: WHOIS Lookup" 
            description="Free, catches large enterprises"
            target="30%"
            color="blue"
          />
          <LayerPerformance 
            name="Layer 2: Multi-API Intelligence" 
            description="IPinfo, ipapi.co, ip-api.com"
            target="+20-25%"
            color="purple"
          />
          <LayerPerformance 
            name="Layer 3: Reverse DNS" 
            description="Extract company from hostname"
            target="+5%"
            color="green"
          />
          <LayerPerformance 
            name="Layer 4: ASN Intelligence" 
            description="Corporate network detection"
            target="+3%"
            color="yellow"
          />
          <LayerPerformance 
            name="Layer 7: Smart Caching" 
            description="Reduces API costs by 50%+"
            target="Cost savings"
            color="indigo"
          />
        </div>
      </div>

      {/* Top Companies Chart */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Top 10 Companies</h2>
        {top_companies && top_companies.length > 0 ? (
          <div className="space-y-4">
            {top_companies.map((company, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-bold text-blue-600">
                      {index + 1}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{company.company}</div>
                      <div className="text-xs text-gray-500">Avg confidence: {company.avg_confidence}%</div>
                    </div>
                  </div>
                  <div className="text-xl font-bold text-blue-600">{company.count}</div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(company.count / top_companies[0].count) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No company data available</p>
        )}
      </div>

      {/* Geographic Distribution */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Geographic Distribution</h2>
        {visitors_by_country && visitors_by_country.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {visitors_by_country.map((country, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                    {country.country?.substring(0, 2) || '??'}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{country.country || 'Unknown'}</div>
                    <div className="text-sm text-gray-500">{country.count} visitors</div>
                  </div>
                </div>
                <div className="text-2xl font-bold text-gray-700">{country.count}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No geographic data available</p>
        )}
      </div>

      {/* Tips for Better Accuracy */}
      <div className="card bg-blue-50 border-blue-200">
        <h2 className="text-lg font-semibold text-blue-900 mb-4">💡 Tips to Improve Identification Rate</h2>
        <div className="space-y-3 text-sm text-blue-800">
          <div className="flex items-start space-x-2">
            <span className="font-bold">1.</span>
            <p>Add API keys (IPinfo, ipapi.co) to unlock premium features and higher accuracy</p>
          </div>
          <div className="flex items-start space-x-2">
            <span className="font-bold">2.</span>
            <p>Enable Clearbit Reveal for B2B lead identification (requires paid subscription)</p>
          </div>
          <div className="flex items-start space-x-2">
            <span className="font-bold">3.</span>
            <p>Corporate office IPs have higher identification rates (80%+) vs residential IPs (10-20%)</p>
          </div>
          <div className="flex items-start space-x-2">
            <span className="font-bold">4.</span>
            <p>Manually correct misidentified companies to improve the learning database</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function LayerPerformance({ name, description, target, color }) {
  const colors = {
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    indigo: 'bg-indigo-500',
  };

  return (
    <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
      <div className={`w-3 h-3 rounded-full ${colors[color]}`}></div>
      <div className="flex-1">
        <div className="font-medium text-gray-900">{name}</div>
        <div className="text-sm text-gray-600">{description}</div>
      </div>
      <div className="text-right">
        <div className="text-sm font-semibold text-gray-700">{target}</div>
        <div className="text-xs text-gray-500">Target</div>
      </div>
    </div>
  );
}

export default Analytics;