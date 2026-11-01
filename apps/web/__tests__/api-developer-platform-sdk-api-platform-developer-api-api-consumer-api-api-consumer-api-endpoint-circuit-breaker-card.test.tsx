import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-circuit-breaker-card";

describe("EndpointCircuitBreakerCard", () => {
  it("shows breakers", () => {
    const breakers = [{ path: "/api/users", state: "closed", failures: 1, threshold: 5 }, { path: "/api/orders", state: "open", failures: 5, threshold: 5 }];
    const { container } = render(<Card breakers={breakers} appName="App" />);
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("5/5 failures");
  });
  it("shows empty", () => {
    const { container } = render(<Card breakers={[]} appName="App" />);
    expect(container.textContent).toContain("No circuit breakers");
  });
});
