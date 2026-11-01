import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RequestQueueCard from "../src/components/api-developer-platform-sdk-consumer-api-request-queue-card";

describe("RequestQueueCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<RequestQueueCard />);
    expect(container.textContent).toContain("Request Queue");
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("Queued");
    expect(container.textContent).toContain("Processing");
  });

  it("shows utilization", () => {
    const { container } = render(<RequestQueueCard />);
    expect(container.textContent).toContain("80% utilization");
    expect(container.textContent).toContain("max 10 concurrent");
  });
});
