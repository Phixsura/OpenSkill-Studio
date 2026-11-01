import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceAnalyzer } from "@/components/trace-analyzer";

describe("TraceAnalyzer", () => {
  it("renders", () => {
    const { container } = render(
      <TraceAnalyzer spanCount={5} totalMs={355} bottleneck="GET /users"
        bottleneckMs={200} services={["api", "db", "cache"]} errorSpans={1} hasErrors={true} />
    );
    expect(container.textContent).toContain("Trace Analysis");
    expect(container.textContent).toContain("5 spans");
    expect(container.textContent).toContain("355ms");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("200ms");
    expect(container.textContent).toContain("1 errors");
  });
});
