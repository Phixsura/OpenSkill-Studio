import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogAggregationView } from "@/components/log-aggregation-view";

describe("LogAggregationView", () => {
  it("renders aggregation", () => {
    const { container } = render(
      <LogAggregationView totalLines={5000} sourceCount={3} errorCount={100}
        errorRate={2} byLevel={{ info: 4500, warn: 400, error: 100 }}
        bySource={{ api: 3000, worker: 1500, scheduler: 500 }} />
    );
    expect(container.textContent).toContain("Log Aggregation");
    expect(container.textContent).toContain("5,000 lines");
    expect(container.textContent).toContain("3 sources");
    expect(container.textContent).toContain("info");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("100 (2%)");
  });
});
