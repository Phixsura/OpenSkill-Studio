import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeCheckMap } from "@/components/uptime-check-map";

describe("UptimeCheckMap", () => {
  const checks = [
    { region: "us-east", status: "up", latency_ms: 35, status_code: 200 },
    { region: "eu-west", status: "up", latency_ms: 80, status_code: 200 },
  ];
  it("renders", () => {
    const { container } = render(
      <UptimeCheckMap endpoint="https://api.example.com" checks={checks} avgLatencyMs={57.5} status="operational" />
    );
    expect(container.textContent).toContain("Uptime Checks");
    expect(container.textContent).toContain("57.5ms");
    expect(container.textContent).toContain("🇺🇸 US East");
    expect(container.textContent).toContain("🇪🇺 Europe");
    expect(container.textContent).toContain("✅");
  });
});
