import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorReporterPanel } from "@/components/error-reporter-panel";

const mockGroups = [
  { fingerprint: "fp1", message: "undefined is not a function", errorType: "TypeError",
    count: 42, firstSeen: "2h ago", lastSeen: "5m ago", resolved: false },
  { fingerprint: "fp2", message: "Network timeout", errorType: "NetworkError",
    count: 8, firstSeen: "1d ago", lastSeen: "1h ago", resolved: true },
];
const mockStats = { totalErrors: 50, uniqueErrors: 2, unresolved: 1, ratePerMinute: 2.5 };

describe("ErrorReporterPanel", () => {
  it("renders error stats", () => {
    const { container } = render(<ErrorReporterPanel groups={mockGroups} stats={mockStats} />);
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("1 unresolved");
    expect(container.textContent).toContain("2.5/min");
  });

  it("shows unresolved by default", () => {
    const { container } = render(<ErrorReporterPanel groups={mockGroups} stats={mockStats} />);
    expect(container.textContent).toContain("undefined is not a function");
    expect(container.textContent).not.toContain("Network timeout");
  });

  it("calls onResolve", () => {
    const onResolve = vi.fn();
    const { getByText } = render(<ErrorReporterPanel groups={mockGroups} stats={mockStats} onResolve={onResolve} />);
    fireEvent.click(getByText("Resolve"));
    expect(onResolve).toHaveBeenCalledWith("fp1");
  });

  it("shows all when filtered", () => {
    const { getByText, container } = render(<ErrorReporterPanel groups={mockGroups} stats={mockStats} />);
    fireEvent.click(getByText("all"));
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("NetworkError");
  });
});
