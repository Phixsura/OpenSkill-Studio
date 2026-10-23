import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PublicStatusPage } from "@/components/public-status-page";

describe("PublicStatusPage", () => {
  it("renders status page", () => {
    const { container } = render(
      <PublicStatusPage title="OpenSkill Status" overall="degraded" allOperational={false}
        components={[
          { name: "API", status: "operational", uptimePct: 99.99 },
          { name: "DB", status: "degraded", uptimePct: 98.5 },
        ]}
        activeIncidents={[
          { title: "DB slow queries", status: "identified", impact: "minor", updated: "5m ago" },
        ]} />
    );
    expect(container.textContent).toContain("OpenSkill Status");
    expect(container.textContent).toContain("Degraded Performance");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("DB slow queries");
    expect(container.textContent).toContain("Active Incidents");
  });
});
