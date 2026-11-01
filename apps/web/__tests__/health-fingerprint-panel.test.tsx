import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthFingerprintPanel } from "@/components/health-fingerprint-panel";
describe("HealthFingerprintPanel", () => {
  it("renders", () => {
    const { container } = render(
      <HealthFingerprintPanel fingerprints={[
        { service: "api", fingerprint: "abc123def456", level: "green", uptime: 99.99, errorRate: 0.1, p99Ms: 100 },
        { service: "db", fingerprint: "xyz789abc012", level: "red", uptime: 95, errorRate: 10, p99Ms: 2000 },
      ]} />
    );
    expect(container.textContent).toContain("Health Fingerprints");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("abc123def456");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("db");
  });
});
