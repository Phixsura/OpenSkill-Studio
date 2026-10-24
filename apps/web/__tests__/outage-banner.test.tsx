import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OutageBanner } from "@/components/outage-banner";

describe("OutageBanner", () => {
  it("renders outage", () => {
    const { container } = render(
      <OutageBanner overallStatus="degraded" activeIncidents={1}
        affectedServices={["api", "db"]} latestMessage="Investigating elevated errors" />
    );
    expect(container.textContent).toContain("Partial System Outage");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("api, db");
    expect(container.textContent).toContain("Investigating");
  });

  it("renders operational", () => {
    const { container } = render(
      <OutageBanner overallStatus="operational" activeIncidents={0}
        affectedServices={[]} latestMessage="" />
    );
    expect(container.textContent).toContain("All Systems Operational");
  });
});
