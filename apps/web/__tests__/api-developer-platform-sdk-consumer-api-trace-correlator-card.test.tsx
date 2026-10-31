import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TraceCorrelatorCard from "../src/components/api-developer-platform-sdk-consumer-api-trace-correlator-card";

describe("TraceCorrelatorCard", () => {
  it("renders title and traces", () => {
    const { container } = render(<TraceCorrelatorCard />);
    expect(container.textContent).toContain("Trace Correlator");
    expect(container.textContent).toContain("abc123");
    expect(container.textContent).toContain("gateway");
  });

  it("shows span count", () => {
    const { container } = render(<TraceCorrelatorCard />);
    expect(container.textContent).toContain("2 traces");
    expect(container.textContent).toContain("13 spans");
  });
});
