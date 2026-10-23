import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorBoundaryFallback } from "@/components/error-boundary-fallback";

describe("ErrorBoundaryFallback", () => {
  it("renders fallback", () => {
    const onAction = vi.fn();
    const { container, getByText } = render(
      <ErrorBoundaryFallback title="Something went wrong" message="Cannot read null"
        showDetails={true} stackPreview="at UserProfile (user.tsx:42)"
        actions={[
          { label: "Retry", action: "retry" },
          { label: "Go Home", action: "navigate", url: "/" },
        ]} onAction={onAction} />
    );
    expect(container.textContent).toContain("Something went wrong");
    expect(container.textContent).toContain("Cannot read null");
    expect(container.textContent).toContain("user.tsx:42");
    fireEvent.click(getByText("Retry"));
    expect(onAction).toHaveBeenCalledWith("retry", undefined);
  });
});
