import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorTrackingDashboard } from "@/components/error-tracking-dashboard";

describe("ErrorTrackingDashboard", () => {
  const groups = [
    { fingerprint: "fp1", message: "NullPointer", count: 15, users_affected: 5, level: "error", last_seen: "2026-10-23" },
  ];
  it("renders", () => {
    const { container } = render(
      <ErrorTrackingDashboard groups={groups} uniqueErrors={1} totalOccurrences={15}
        trend="increasing" onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Error Tracking");
    expect(container.textContent).toContain("NullPointer");
    expect(container.textContent).toContain("15×");
    expect(container.textContent).toContain("📈");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(
      <ErrorTrackingDashboard groups={groups} uniqueErrors={1} totalOccurrences={15}
        trend="stable" onSelect={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("fp1");
  });
});
