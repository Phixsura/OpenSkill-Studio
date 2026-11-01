import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcHealthMatrix } from "@/components/svc-health-matrix";

describe("SvcHealthMatrix", () => {
  it("renders", () => {
    const { container } = render(
      <SvcHealthMatrix healthPct={50} weakest="worker"
        matrix={[
          { service: "api", status: "healthy", score: 4, dimensions: { uptime: true, latency: true, errors: true, saturation: true } },
          { service: "worker", status: "unhealthy", score: 1, dimensions: { uptime: false, latency: false, errors: false, saturation: true } },
        ]} />
    );
    expect(container.textContent).toContain("Health Matrix");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("weakest: worker");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("worker");
  });
});
