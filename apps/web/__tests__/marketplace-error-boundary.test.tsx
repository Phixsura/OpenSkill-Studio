import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceErrorBoundary } from "@/components/marketplace-error-boundary";

function ThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) throw new Error("Test explosion");
  return <div>Content loaded</div>;
}

describe("MarketplaceErrorBoundary", () => {
  // Suppress console.error for expected error boundary logs
  const originalError = console.error;
  beforeAll(() => { console.error = vi.fn(); });
  afterAll(() => { console.error = originalError; });

  it("renders children when no error", () => {
    const { container } = render(
      <MarketplaceErrorBoundary>
        <div>Hello World</div>
      </MarketplaceErrorBoundary>
    );
    expect(container.textContent).toContain("Hello World");
  });

  it("renders fallback on error", () => {
    const onError = vi.fn();
    const { container } = render(
      <MarketplaceErrorBoundary fallbackTitle="Extension Error" onError={onError}>
        <ThrowingComponent shouldThrow={true} />
      </MarketplaceErrorBoundary>
    );
    expect(container.textContent).toContain("Extension Error");
    expect(container.textContent).toContain("Test explosion");
    expect(onError).toHaveBeenCalled();
  });

  it("shows retry button", () => {
    const onRetry = vi.fn();
    const { getByText } = render(
      <MarketplaceErrorBoundary onRetry={onRetry}>
        <ThrowingComponent shouldThrow={true} />
      </MarketplaceErrorBoundary>
    );
    expect(getByText("🔄 Try Again")).toBeDefined();
  });
});
