import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-request-queue-card";

describe("RequestQueueCard", () => {
  it("shows stats", () => {
    const stats = { queued: 15, processing: 5, completed: 100, failed: 3 };
    const { container } = render(<Card stats={stats} maxSize={1000} appName="App" />);
    expect(container.textContent).toContain("Request Queue");
    expect(container.textContent).toContain("20/1000 active");
    expect(container.textContent).toContain("15");
    expect(container.textContent).toContain("100");
  });
  it("shows zero", () => {
    const stats = { queued: 0, processing: 0, completed: 0, failed: 0 };
    const { container } = render(<Card stats={stats} maxSize={100} appName="App" />);
    expect(container.textContent).toContain("0/100");
  });
});
