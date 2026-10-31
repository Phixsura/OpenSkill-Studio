import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerfFlameGraph } from "@/components/perf-flame-graph";

describe("PerfFlameGraph", () => {
  it("renders profile", () => {
    const { container } = render(
      <PerfFlameGraph totalMs={380} bottleneck="db_query" improvementPct={30}
        spans={[
          { name: "db_query", selfMs: 150, durationMs: 150, pct: 39.5 },
          { name: "serialize", selfMs: 30, durationMs: 30, pct: 7.9 },
          { name: "handler", selfMs: 20, durationMs: 200, pct: 5.3 },
        ]} />
    );
    expect(container.textContent).toContain("Performance Profile");
    expect(container.textContent).toContain("380ms");
    expect(container.textContent).toContain("bottleneck: db_query");
    expect(container.textContent).toContain("30%");
    expect(container.textContent).toContain("150ms");
  });
});
