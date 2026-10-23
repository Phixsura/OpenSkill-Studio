import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusPageView } from "@/components/status-page-view";

describe("StatusPageView", () => {
  it("renders status page", () => {
    const { container } = render(
      <StatusPageView title="MyApp Status" overall="operational" avgUptime={99.97} incidentCount={0}
        components={[
          { name: "API", status: "operational", uptimePct: 99.99 },
          { name: "Web", status: "operational", uptimePct: 99.95 },
        ]} />
    );
    expect(container.textContent).toContain("MyApp Status");
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("99.97%");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("Web");
  });
});
