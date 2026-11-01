import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiHealthReport } from "@/components/api-health-report";

describe("ApiHealthReport", () => {
  it("renders report", () => {
    const { container } = render(
      <ApiHealthReport grade="A" healthPct={90} totalEndpoints={10} healthy={9}
        degraded={1} unhealthy={0} totalRps={5000} avgLatencyMs={150} avgErrorRate={0.5} />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("150ms");
    expect(container.textContent).toContain("9 healthy");
    expect(container.textContent).toContain("1 degraded");
  });
});
