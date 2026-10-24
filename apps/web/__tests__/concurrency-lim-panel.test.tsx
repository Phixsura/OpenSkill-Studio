import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConcurrencyLimPanel } from "@/components/concurrency-lim-panel";
describe("ConcurrencyLimPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ConcurrencyLimPanel rejected={50}
        services={[
          { service: "api", active: 8, limit: 10 },
          { service: "worker", active: 5, limit: 5 },
        ]} />
    );
    expect(container.textContent).toContain("Concurrency Limiter");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("50 rejected");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("8/10");
    expect(container.textContent).toContain("5/5");
  });
});
