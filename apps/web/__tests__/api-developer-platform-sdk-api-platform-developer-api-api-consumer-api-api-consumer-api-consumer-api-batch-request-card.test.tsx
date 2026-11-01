import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-batch-request-card";

describe("ConsumerApiBatchRequestCard", () => {
  it("shows batch results", () => {
    const results = [{ itemId: "1", method: "GET", path: "/api/users", status: 200, error: null }];
    const { container } = render(<Card results={results} total={2} succeeded={1} failed={1} totalBatches={5} totalItems={25} appName="App" />);
    expect(container.textContent).toContain("Batch Requests");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("5 batches");
  });
  it("shows counts", () => {
    const { container } = render(<Card results={[]} total={10} succeeded={8} failed={2} totalBatches={1} totalItems={10} appName="App" />);
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("8");
  });
});
