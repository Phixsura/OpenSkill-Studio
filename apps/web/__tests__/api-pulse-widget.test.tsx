import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiPulseWidget } from "@/components/api-pulse-widget";

describe("ApiPulseWidget", () => {
  it("renders", () => {
    const { container } = render(
      <ApiPulseWidget healthy={10} total={10} avgLatencyMs={65}
        totalRps={5000} errorCount={3} pulse="strong" />
    );
    expect(container.textContent).toContain("API Pulse");
    expect(container.textContent).toContain("strong");
    expect(container.textContent).toContain("10/10");
    expect(container.textContent).toContain("65ms");
    expect(container.textContent).toContain("5,000");
  });
});
