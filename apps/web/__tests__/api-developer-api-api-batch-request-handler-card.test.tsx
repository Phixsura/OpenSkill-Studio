import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiBatchRequestHandlerCard from "../src/components/api-developer-api-api-batch-request-handler-card";

const batches = [
  { batch_id: "b1", total: 10, succeeded: 9, failed: 1 },
  { batch_id: "b2", total: 5, succeeded: 5, failed: 0 },
];

describe("APIDeveloperAPIApiBatchRequestHandlerCard", () => {
  it("shows batches", () => {
    const { container } = render(<APIDeveloperAPIApiBatchRequestHandlerCard batches={batches} avgBatchSize={7.5} appName="App" />);
    expect(container.textContent).toContain("Batch Requests");
    expect(container.textContent).toContain("avg size: 7.5");
    expect(container.textContent).toContain("b1");
    expect(container.textContent).toContain("9 ok");
    expect(container.textContent).toContain("1 fail");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiBatchRequestHandlerCard batches={[]} avgBatchSize={0} appName="App" />);
    expect(container.textContent).toContain("No batch requests");
  });
});
