import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIBatchRequestCard from "../src/components/api-batch-request-card";

const batches = [
  { batch_id: "b1", total: 5, success_count: 4, failure_count: 1, all_complete: true },
  { batch_id: "b2", total: 3, success_count: 1, failure_count: 0, all_complete: false },
];

describe("APIBatchRequestCard", () => {
  it("renders header and batch count", () => {
    const { container } = render(<APIBatchRequestCard batches={batches} appName="App" />);
    expect(container.textContent).toContain("Batch Requests");
    expect(container.textContent).toContain("2 batches");
  });

  it("shows batch results", () => {
    const { container } = render(<APIBatchRequestCard batches={batches} appName="App" />);
    expect(container.textContent).toContain("4/5 ok");
    expect(container.textContent).toContain("1/3 ok");
  });

  it("shows empty state", () => {
    const { container } = render(<APIBatchRequestCard batches={[]} appName="App" />);
    expect(container.textContent).toContain("No batch requests");
  });
});
