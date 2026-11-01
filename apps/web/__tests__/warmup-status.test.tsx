import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WarmupStatus } from "@/components/warmup-status";

describe("WarmupStatus", () => {
  it("renders", () => {
    const { container } = render(
      <WarmupStatus allReady={false} ready={2} total={3} services={[
        { name: "api", ready: true, latencyMs: 50, thresholdMs: 500 },
        { name: "db", ready: true, latencyMs: 10, thresholdMs: 100 },
        { name: "cache", ready: false, latencyMs: 5000, thresholdMs: 100 },
      ]} />
    );
    expect(container.textContent).toContain("Warm-up Status");
    expect(container.textContent).toContain("2/3 ready");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("50ms");
    expect(container.textContent).toContain("cache");
  });
});
