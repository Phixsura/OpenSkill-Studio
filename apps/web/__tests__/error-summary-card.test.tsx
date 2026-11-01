import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorSummaryCard } from "@/components/error-summary-card";

describe("ErrorSummaryCard", () => {
  it("shows no errors state", () => {
    const { container } = render(<ErrorSummaryCard summary={{ total: 0, by_type: {}, unique_types: 0 }} />);
    expect(container.textContent).toContain("No errors");
  });

  it("shows error count", () => {
    const { container } = render(<ErrorSummaryCard summary={{ total: 5, by_type: { TypeError: 3, ValueError: 2 }, unique_types: 2 }} />);
    expect(container.textContent).toContain("5 Errors");
  });

  it("shows error types", () => {
    const { container } = render(<ErrorSummaryCard summary={{ total: 3, by_type: { TypeError: 3 }, unique_types: 1 }} />);
    expect(container.textContent).toContain("TypeError");
  });

  it("shows unique type count", () => {
    const { container } = render(<ErrorSummaryCard summary={{ total: 5, by_type: { A: 3, B: 2 }, unique_types: 2 }} />);
    expect(container.textContent).toContain("2 types");
  });

  it("includes app name", () => {
    const { container } = render(<ErrorSummaryCard summary={{ total: 0, by_type: {}, unique_types: 0 }} appName="Test App" />);
    expect(container.textContent).toContain("Test App");
  });
});
