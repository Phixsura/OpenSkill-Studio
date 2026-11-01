import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-bulkhead-card";

describe("RequestBulkheadCard", () => {
  it("shows partitions", () => {
    const parts = [{ partition_id: "p1", name: "Critical", max_concurrent: 10, active: 7, rejected: 3, utilization: 70 }];
    const { container } = render(<Card partitions={parts} appName="App" />);
    expect(container.textContent).toContain("Request Bulkhead");
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("7/10");
    expect(container.textContent).toContain("3 rejected");
  });
  it("shows empty", () => {
    const { container } = render(<Card partitions={[]} appName="App" />);
    expect(container.textContent).toContain("No bulkhead partitions");
  });
});
