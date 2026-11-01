import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SessionAnalyticsPanel } from "@/components/session-analytics-panel";

describe("SessionAnalyticsPanel", () => {
  it("renders analytics", () => {
    const { container } = render(
      <SessionAnalyticsPanel totalSessions={1500} avgDurationSec={150} avgPages={6.2}
        bounceRate={33.3} bySource={{ google: 800, direct: 500, twitter: 200 }} />
    );
    expect(container.textContent).toContain("Session Analytics");
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("150s");
    expect(container.textContent).toContain("33.3%");
    expect(container.textContent).toContain("google");
    expect(container.textContent).toContain("direct");
  });
});
