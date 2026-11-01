import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SliCollectDash } from "@/components/sli-collect-dash";

describe("SliCollectDash", () => {
  it("renders", () => {
    const { container } = render(
      <SliCollectDash slis={[
        { sli: "latency_ms", count: 1000, avg: 45.2, p99: 200, goodPct: 99.5 },
        { sli: "error_rate", count: 1000, avg: 0.5, p99: 2.0, goodPct: 95.0 },
      ]} />
    );
    expect(container.textContent).toContain("SLI Dashboard");
    expect(container.textContent).toContain("2 indicators");
    expect(container.textContent).toContain("latency_ms");
    expect(container.textContent).toContain("avg: 45.2");
    expect(container.textContent).toContain("99.5% good");
    expect(container.textContent).toContain("95% good");
  });
});
