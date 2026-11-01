import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceCorrPanel } from "@/components/trace-corr-panel";

describe("TraceCorrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TraceCorrPanel totalTraces={2} totalSpans={5}
        traces={[
          { traceId: "t2", spans: 1, services: ["api"], durationMs: 2000 },
          { traceId: "t1", spans: 2, services: ["api", "db"], durationMs: 100 },
        ]} />
    );
    expect(container.textContent).toContain("Trace Correlator");
    expect(container.textContent).toContain("2 traces");
    expect(container.textContent).toContain("5 spans");
    expect(container.textContent).toContain("t2");
    expect(container.textContent).toContain("2000ms");
    expect(container.textContent).toContain("api, db");
  });
});
