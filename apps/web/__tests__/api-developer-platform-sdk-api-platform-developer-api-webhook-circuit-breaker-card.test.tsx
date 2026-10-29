import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-webhook-circuit-breaker-card";

describe("CircuitBreakerCard", () => {
  it("shows breakers", () => {
    const breakers = [{ consumer_id: "c1", state: "open", failure_count: 5, success_count: 0 }];
    const { container } = render(<Card breakers={breakers} openCount={1} appName="App" />);
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("5F/0S");
  });
  it("shows empty", () => {
    const { container } = render(<Card breakers={[]} openCount={0} appName="App" />);
    expect(container.textContent).toContain("No circuit breakers");
  });
});
