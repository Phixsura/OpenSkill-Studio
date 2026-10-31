import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-coalescer-card";

describe("RequestCoalescerCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card coalesceRate={35} totalRequests={10000} coalesced={3500} pendingCount={5} appName="App" />);
    expect(container.textContent).toContain("Request Coalescer");
    expect(container.textContent).toContain("35% saved");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("3,500");
  });
  it("shows zero", () => {
    const { container } = render(<Card coalesceRate={0} totalRequests={0} coalesced={0} pendingCount={0} appName="App" />);
    expect(container.textContent).toContain("0% saved");
  });
});
