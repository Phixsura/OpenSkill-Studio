import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-error-distribution-card";

describe("EndpointErrorDistributionCard", () => {
  it("shows distribution", () => {
    const buckets = [{ statusCode: 429, errorCode: "RATE_LIMITED", count: 80, percentage: 80 }, { statusCode: 500, errorCode: "INTERNAL", count: 20, percentage: 20 }];
    const { container } = render(<Card endpoint="/api/users" totalErrors={100} errorRate={5} buckets={buckets} mostCommon="RATE_LIMITED" appName="App" />);
    expect(container.textContent).toContain("Error Distribution");
    expect(container.textContent).toContain("RATE_LIMITED");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("🔴");
  });
  it("shows no errors", () => {
    const { container } = render(<Card endpoint="/api" totalErrors={0} errorRate={0} buckets={[]} mostCommon="" appName="App" />);
    expect(container.textContent).toContain("No errors!");
  });
});
