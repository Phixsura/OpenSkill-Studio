import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RetryQueueCard from "../src/components/api-developer-platform-sdk-consumer-api-retry-queue-card";

describe("RetryQueueCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<RetryQueueCard />);
    expect(container.textContent).toContain("Retry Queue");
    expect(container.textContent).toContain("Pending");
    expect(container.textContent).toContain("Retrying");
    expect(container.textContent).toContain("Dead");
  });

  it("shows total count", () => {
    const { container } = render(<RetryQueueCard />);
    expect(container.textContent).toContain("24 total deliveries");
  });
});
