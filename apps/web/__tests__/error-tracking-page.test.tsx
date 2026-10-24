import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorTrackingPage } from "@/components/error-tracking-page";

describe("ErrorTrackingPage", () => {
  const groups = [{ fingerprint: "abc", type: "TypeError", message: "undefined is not a function",
    count: 42, affectedUsers: 15, lastSeen: "2026-10-24" }];
  it("renders errors", () => {
    const { container } = render(
      <ErrorTrackingPage groups={groups} totalErrors={42} uniqueErrors={1}
        period="24h" errorRateTrend="up" />
    );
    expect(container.textContent).toContain("Error Tracking");
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("42×");
    expect(container.textContent).toContain("15 users");
    expect(container.textContent).toContain("Rising");
  });
});
