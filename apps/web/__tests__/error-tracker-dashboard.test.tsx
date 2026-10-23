import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorTrackerDashboard } from "@/components/error-tracker-dashboard";

describe("ErrorTrackerDashboard", () => {
  const groups = [
    { fingerprint: "abc", message: "TypeError: undefined", count: 15, firstSeen: "2026-01-01", lastSeen: "2026-01-03", affectedUsers: 8 },
  ];
  it("renders errors", () => {
    const { container } = render(
      <ErrorTrackerDashboard groups={groups} totalErrors={15} uniqueErrors={1} />
    );
    expect(container.textContent).toContain("TypeError: undefined");
    expect(container.textContent).toContain("15×");
    expect(container.textContent).toContain("8 users");
    expect(container.textContent).toContain("15 total");
  });
});
