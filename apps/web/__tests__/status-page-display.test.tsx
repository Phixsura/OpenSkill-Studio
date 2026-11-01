import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusPageDisplay } from "@/components/status-page-display";

describe("StatusPageDisplay", () => {
  const components = [
    { name: "API", status: "operational" },
    { name: "CDN", status: "degraded" },
  ];
  it("renders", () => {
    const { container } = render(
      <StatusPageDisplay appName="MyApp" overallStatus="degraded" components={components}
        lastUpdated="2026-10-23T12:00:00" />
    );
    expect(container.textContent).toContain("MyApp");
    expect(container.textContent).toContain("Degraded");
    expect(container.textContent).toContain("🟡");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("Operational");
  });
});
