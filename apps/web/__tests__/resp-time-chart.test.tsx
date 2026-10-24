import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RespTimeChart } from "@/components/resp-time-chart";

describe("RespTimeChart", () => {
  it("renders chart", () => {
    const { container } = render(
      <RespTimeChart slowest="/slow" endpoints={[
        { endpoint: "/slow", avgMs: 800, p99Ms: 1200, slowPct: 60, count: 100 },
        { endpoint: "/fast", avgMs: 20, p99Ms: 50, slowPct: 0, count: 500 },
      ]} />
    );
    expect(container.textContent).toContain("Response Times");
    expect(container.textContent).toContain("slowest: /slow");
    expect(container.textContent).toContain("avg 800ms");
    expect(container.textContent).toContain("/fast");
    expect(container.textContent).toContain("50ms");
  });
});
