import React from 'react';

export default function RenderTable({ tableData }) {
  if (!tableData || !Array.isArray(tableData) || tableData.length === 0) {
    return null;
  }

  const headers = Object.keys(tableData[0]);

  return (
    <div style={{ overflowX: 'auto', width: '100%' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left'}}>
        <thead>
          <tr style={{ borderBottom: '2px solid #ccc', textTransform: 'capitalize' }}>
            {headers.map((header) => (
              <th key={header} style={{ padding: '8px 12px' }}>
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tableData.map((row, rowIdx) => (
            <tr key={rowIdx} style={{ borderBottom: '1px solid #ccc' }}>
              {headers.map((header) => (
                <td key={header} style={{ padding: '8px 12px' }}>
                  {row[header]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}