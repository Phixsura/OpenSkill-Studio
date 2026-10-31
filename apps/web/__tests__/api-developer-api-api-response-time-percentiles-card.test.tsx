import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiResponseTimePercentilesCard from "../src/components/api-developer-api-api-response-time-percentiles-card";

const percentiles = [
  { endpoint: "/api/users", p50: 25, p90: 80, p95: 120, p99: 250, count: 10000 },
];

describe("APIDeveloperAPIApiResponseTimePercentilesCard", () => {
  it("shows percentiles", () => {
    const { container } = render(<APIDeveloperAPIApiResponseTimePercentilesCard percentiles={percentiles} appName="App" />);
    expect(container.textContent).toContain("Response Percentiles");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("25ms");
    expect(container.textContent).toContain("250ms");
    expect(container.textContent).toContain("p99");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiResponseTimePercentilesCard percentiles={[]} appName="App" />);
    expect(container.textContent).toContain("No data");
  });
});
