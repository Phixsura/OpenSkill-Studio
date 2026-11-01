import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthAttestPanel } from "@/components/health-attest-panel";
describe("HealthAttestPanel", () => {
  it("renders", () => {
    const { container } = render(
      <HealthAttestPanel healthy={1} stale={1}
        services={[
          { service: "api", status: "healthy", stale: false, ageSeconds: 5 },
          { service: "worker", status: "stale", stale: true, ageSeconds: 120 },
        ]} />
    );
    expect(container.textContent).toContain("Health Attestation");
    expect(container.textContent).toContain("1 healthy");
    expect(container.textContent).toContain("1 stale");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("worker");
    expect(container.textContent).toContain("120s ago");
  });
});
