import React, { useState, useMemo } from 'react';

interface JsonViewerProps {
  data: unknown;
  maxHeight?: string;
}

const JsonViewer: React.FC<JsonViewerProps> = ({ data, maxHeight = '400px' }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const jsonString = useMemo(() => {
    try {
      return JSON.stringify(data, null, 2);
    } catch (error) {
      return String(data);
    }
  }, [data]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(jsonString);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const syntaxHighlight = (json: string): string => {
    return json
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match) => {
        let cls = 'json-number';
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = 'json-key';
          } else {
            cls = 'json-string';
          }
        } else if (/true|false/.test(match)) {
          cls = 'json-boolean';
        } else if (/null/.test(match)) {
          cls = 'json-null';
        }
        return `<span class="${cls}">${match}</span>`;
      });
  };

  const highlightedJson = useMemo(() => syntaxHighlight(jsonString), [jsonString]);

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0.75rem 1rem',
          background: 'var(--color-slate-900)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <span style={{ fontSize: '0.75rem', color: 'var(--color-gray-400)', fontWeight: 600, textTransform: 'uppercase' }}>
          JSON Data
        </span>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className="btn btn-sm"
            onClick={handleCopy}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            {copied ? '✓ Copied' : '📋 Copy'}
          </button>
          <button
            className="btn btn-sm"
            onClick={() => setIsExpanded(!isExpanded)}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            {isExpanded ? '▼ Collapse' : '▶ Expand'}
          </button>
        </div>
      </div>
      <div
        style={{
          background: '#0b1224',
          color: '#e5e7eb',
          padding: '1rem',
          overflow: 'auto',
          maxHeight: isExpanded ? 'none' : maxHeight,
          fontFamily: 'var(--font-mono)',
          fontSize: '0.875rem',
          lineHeight: 1.6,
        }}
      >
        <style>
          {`
            .json-key { color: #7dd3fc; }
            .json-string { color: #86efac; }
            .json-number { color: #fbbf24; }
            .json-boolean { color: #a78bfa; }
            .json-null { color: #f87171; }
          `}
        </style>
        <pre
          style={{
            margin: 0,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
          dangerouslySetInnerHTML={{ __html: highlightedJson }}
        />
      </div>
    </div>
  );
};

export default JsonViewer;
