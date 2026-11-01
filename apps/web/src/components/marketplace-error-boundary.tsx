"use client";

import { Component, type ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallbackTitle?: string;
  onError?: (error: Error, info: string) => void;
  onRetry?: () => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: string;
}

export class MarketplaceErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: "" };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    const errorInfo = info.componentStack || "";
    this.setState({ errorInfo });
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: "" });
    this.props.onRetry?.();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10 p-6 text-center space-y-4">
          <div className="text-4xl">⚠️</div>
          <h3 className="text-lg font-bold text-red-700 dark:text-red-300">
            {this.props.fallbackTitle || "Something went wrong"}
          </h3>
          <p className="text-sm text-red-600 dark:text-red-400">
            {this.state.error?.message || "An unexpected error occurred"}
          </p>
          {this.state.errorInfo && (
            <details className="text-left">
              <summary className="text-xs text-red-400 cursor-pointer">Technical details</summary>
              <pre className="mt-2 text-xs bg-red-100 dark:bg-red-900/30 p-2 rounded overflow-auto max-h-32">
                {this.state.errorInfo}
              </pre>
            </details>
          )}
          <button
            onClick={this.handleRetry}
            className="rounded-lg bg-red-600 text-white px-4 py-2 text-sm font-medium hover:bg-red-700"
          >
            🔄 Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Functional wrapper for use in server components
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  fallbackTitle?: string,
) {
  return function WithErrorBoundary(props: P) {
    return (
      <MarketplaceErrorBoundary fallbackTitle={fallbackTitle}>
        <WrappedComponent {...props} />
      </MarketplaceErrorBoundary>
    );
  };
}
