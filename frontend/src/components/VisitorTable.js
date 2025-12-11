import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function VisitorTable({ visitors, onRefresh }) {
  const [filter, setFilter] = useState({ hideISP: false, search: '' });

  const filteredVisitors = visitors.filter(visitor => {
    if (filter.hideISP && visitor.is_isp) return false;
    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      return (
        visitor.company_name?.toLowerCase().includes(searchLower) ||
        visitor.ip_address?.toLowerCase().includes(searchLower) ||
        visitor.country?.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  return (
    <div className="space-y-6" data-testid="visitor-table">
      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by company, IP, or country..."
              value={filter.search}
              onChange={(e) => setFilter({ ...filter, search: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              data-testid="search-input"
            />
          </div>
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filter.hideISP}
              onChange={(e) => setFilter({ ...filter, hideISP: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              data-testid="hide-isp-checkbox"
            />
            <span className="text-sm font-medium text-gray-700">Hide ISPs</span>
          </label>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="text-2xl font-bold text-blue-600">{visitors.length}</div>
          <div className="text-sm text-gray-600">Total Visitors</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-green-600">
            {visitors.filter(v => !v.is_isp && v.company_name).length}
          </div>
          <div className="text-sm text-gray-600">Companies Identified</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-orange-600">
            {visitors.filter(v => v.is_isp).length}
          </div>
          <div className="text-sm text-gray-600">ISP Visitors</div>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Company Name</th>
                <th>IP Address</th>
                <th>Location</th>
                <th>Method</th>
                <th>Confidence</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {filteredVisitors.map((visitor) => (
                <tr key={visitor.id || visitor._id} className="hover:bg-gray-50 transition-colors">
                  <td>
                    <div className="flex flex-col">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900">
                          {visitor.company_name || 'Unknown'}
                        </span>
                        {visitor.is_isp && (
                          <span className="badge badge-warning">ISP</span>
                        )}
                      </div>
                      {visitor.org && visitor.org !== visitor.company_name && (
                        <span className="text-xs text-gray-500 mt-1">{visitor.org}</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="font-mono text-sm">{visitor.ip_address}</div>
                    {visitor.reverse_dns && (
                      <div className="text-xs text-gray-500 mt-1">{visitor.reverse_dns}</div>
                    )}
                  </td>
                  <td>
                    <div className="text-sm">
                      {visitor.city && <div>{visitor.city}</div>}
                      <div className="text-gray-500">{visitor.country || 'N/A'}</div>
                    </div>
                  </td>
                  <td>
                    <MethodBadge method={visitor.identification_method} />
                  </td>
                  <td>
                    <ConfidenceScore score={visitor.confidence_score} />
                  </td>
                  <td className="text-sm text-gray-600">
                    {new Date(visitor.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredVisitors.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No visitors found matching your filters.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function MethodBadge({ method }) {
  const badges = {
    whois: { label: 'WHOIS', color: 'badge-info' },
    reverse_dns: { label: 'DNS', color: 'badge-success' },
    asn: { label: 'ASN', color: 'badge-success' },
    ipinfo: { label: 'IPinfo', color: 'badge-warning' },
    ipapi_co: { label: 'ipapi.co', color: 'badge-warning' },
    ip_api_com: { label: 'ip-api', color: 'badge-warning' },
    multi_api_consensus: { label: 'Multi-API', color: 'badge-success' },
    cache: { label: 'Cached', color: 'badge-info' },
  };

  const badge = badges[method] || { label: method || 'Unknown', color: 'badge-info' };

  return <span className={`badge ${badge.color}`}>{badge.label}</span>;
}

function ConfidenceScore({ score }) {
  const percentage = Math.round(score * 100);
  const color = percentage >= 80 ? 'text-green-600' : percentage >= 60 ? 'text-yellow-600' : 'text-red-600';
  const bgColor = percentage >= 80 ? 'bg-green-500' : percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500';
  
  return (
    <div className="flex flex-col items-start">
      <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden mb-1">
        <div 
          className={`h-full ${bgColor} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      <span className={`text-sm font-medium ${color}`}>{percentage}%</span>
    </div>
  );
}

export default VisitorTable;