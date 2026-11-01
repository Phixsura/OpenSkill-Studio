import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-status-code-analytics-card";

describe("StatusCodeAnalyticsCard", () => {
  it("shows analytics", () => {
    const topCodes = [{ statusCode: 200, count: 800, percentage: 80, category: "2xx" }, { statusCode: 500, count: 100, percentage: 10, category: "5xx" }];
    const { container } = render(<Card totalRequests={1000} successRate={80} clientErrorRate={10} serverErrorRate={10} byCategory={{ "2xx": 800, "4xx": 100, "5xx": 100 }} topCodes={topCodes} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Status Code Analytics");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
  it("shows empty", () => {
    const { container } = render(<Card totalRequests={0} successRate={100} clientErrorRate={0} serverErrorRate={0} byCategory={{}} topCodes={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("0");
  });
});
