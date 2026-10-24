import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GrandSummaryDash } from "@/components/grand-summary-dash";

describe("GrandSummaryDash", () => {
  it("renders", () => {
    const { container } = render(
      <GrandSummaryDash totalServices={1480} totalComponents={1480} allOperational={true}
        modules={[
          { name: "Extension SDK", services: 148, status: "operational", description: "Build extensions" },
          { name: "Security", services: 148, status: "operational", description: "Auth & compliance" },
        ]} />
    );
    expect(container.textContent).toContain("Platform Overview");
    expect(container.textContent).toContain("All Operational");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("Build extensions");
  });
});
