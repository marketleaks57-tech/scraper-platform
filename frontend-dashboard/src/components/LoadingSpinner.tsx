import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', message }) => {
  const sizeClasses = {
    sm: '16px',
    md: '24px',
    lg: '32px',
  };

  return (
    <div className="loading">
      <div className="flex" style={{ flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
        <div
          className="spinner"
          style={{
            width: sizeClasses[size],
            height: sizeClasses[size],
          }}
        />
        {message && <p className="text-gray-500">{message}</p>}
      </div>
    </div>
  );
};

export default LoadingSpinner;

