import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorBoundaryFallback } from "@/components/error-boundary-fallback";

describe("ErrorBoundaryFallback", () => {
  const actions = [{ label: "Refresh", action: "reload" }, { label: "Home", action: "navigate", url: "/" }];
  it("renders", () => {
    const { container } = render(
      <ErrorBoundaryFallback title="Oops" message="Something broke" icon="💥"
        actions={actions} showStackTrace={false} onAction={vi.fn()} />
    );
    expect(container.textContent).toContain("💥");
    expect(container.textContent).toContain("Oops");
    expect(container.textContent).toContain("Something broke");
    expect(container.textContent).toContain("Refresh");
    expect(container.textContent).toContain("Home");
  });
  it("shows stack trace", () => {
    const { container } = render(
      <ErrorBoundaryFallback title="X" message="Y" icon="💥" actions={[]}
        showStackTrace={true} error="TypeError: undefined" onAction={vi.fn()} />
    );
    expect(container.textContent).toContain("TypeError: undefined");
  });
  it("action click", () => {
    const fn = vi.fn();
    const { container } = render(
      <ErrorBoundaryFallback title="X" message="Y" icon="💥" actions={actions}
        showStackTrace={false} onAction={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Refresh")!);
    expect(fn).toHaveBeenCalledWith("reload", undefined);
  });
});
