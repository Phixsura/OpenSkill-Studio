import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-profiler-card";

describe("RequestProfilerCard", () => {
  it("shows profiles", () => {
    const profiles = [{ endpoint: "/users", method: "GET", avg_ms: 75, min_ms: 50, max_ms: 100, samples: 1000, error_pct: 2.5 }];
    const { container } = render(<Card profiles={profiles} appName="App" />);
    expect(container.textContent).toContain("Request Profiler");
    expect(container.textContent).toContain("avg: 75ms");
    expect(container.textContent).toContain("1,000 reqs");
    expect(container.textContent).toContain("2.5% err");
  });
  it("shows empty", () => {
    const { container } = render(<Card profiles={[]} appName="App" />);
    expect(container.textContent).toContain("No profiling data");
  });
});
