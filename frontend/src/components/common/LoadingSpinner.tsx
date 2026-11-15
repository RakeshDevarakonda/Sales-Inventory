import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading data...',
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 animate-in fade-in duration-200">
      <div
        className={`${sizeClasses[size]} border-slate-900 border-t-transparent rounded-full animate-spin`}
      />
      {message && (
        <p className="mt-3 text-xs font-medium text-slate-500 animate-pulse tracking-wide">
          {message}
        </p>
      )}
    </div>
  );
};

export const LoadingOverlay: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => {
  return (
    <div className="fixed inset-0 z-50 bg-white/70 backdrop-blur-xs flex flex-col items-center justify-center animate-in fade-in duration-150">
      <div className="w-10 h-10 border-3 border-slate-900 border-t-transparent rounded-full animate-spin" />
      <p className="mt-3 text-xs font-semibold text-slate-700 tracking-wide">{message}</p>
    </div>
  );
};
