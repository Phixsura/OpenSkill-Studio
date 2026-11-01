import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigAuditCard } from "@/components/config-audit-card";

describe("ConfigAuditCard", () => {
  it("renders", () => {
    const { container } = render(
      <ConfigAuditCard service="api" score={6} total={7} compliancePct={86} grade="B"
        findings={[{ practice: "tracing_enabled", description: "Enable tracing" }]} />
    );
    expect(container.textContent).toContain("Config Audit: api");
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("6/7");
    expect(container.textContent).toContain("86%");
    expect(container.textContent).toContain("tracing enabled");
    expect(container.textContent).toContain("Enable tracing");
  });
});
