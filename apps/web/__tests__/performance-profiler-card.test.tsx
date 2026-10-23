import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerformanceProfilerCard } from "@/components/performance-profiler-card";

describe("PerformanceProfilerCard", () => {
  it("renders profile", () => {
    const { container } = render(
      <PerformanceProfilerCard totalMs={800}
        hotspots={[{ name: "db_query", duration_ms: 500, type: "db" }]}
        suggestions={["Add indexes"]} />
    );
    expect(container.textContent).toContain("800ms");
    expect(container.textContent).toContain("db_query");
    expect(container.textContent).toContain("Add indexes");
  });
});
