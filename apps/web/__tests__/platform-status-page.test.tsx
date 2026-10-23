import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStatusPage } from "@/components/platform-status-page";

describe("PlatformStatusPage", () => {
  const groups = {
    Core: [{ id: "api", name: "API Gateway", status: "operational", icon: "🟢" }],
  };
  it("renders status page", () => {
    const { container } = render(
      <PlatformStatusPage groups={groups} overall="operational" overallLabel="All Systems Operational"
        healthy={1} incidents={[]} updatedAt="2026-01-01T12:00:00Z" />
    );
    expect(container.textContent).toContain("All Systems Operational");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("Core");
    expect(container.textContent).toContain("🟢");
  });
});
