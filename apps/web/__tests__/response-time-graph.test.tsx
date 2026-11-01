import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResponseTimeGraph } from "@/components/response-time-graph";

describe("ResponseTimeGraph", () => {
  it("renders graph", () => {
    const { container } = render(
      <ResponseTimeGraph avg={95} p50={80} p95={200} p99={350}
        slaPct={90} slaMet={false} status="ok" slams={200} />
    );
    expect(container.textContent).toContain("Response Time");
    expect(container.textContent).toContain("ok");
    expect(container.textContent).toContain("SLA: 90%");
    expect(container.textContent).toContain("95ms");
    expect(container.textContent).toContain("P99");
    expect(container.textContent).toContain("350ms");
  });
});
