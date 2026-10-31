import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CircuitBreakerCard from "../src/components/circuit-breaker-card";

const breakers = [
  {
    breaker_id: "cb1",
    service_name: "Payment API",
    state: "closed" as const,
    failure_count: 1,
    failure_threshold: 5,
    success_count: 200,
  },
  {
    breaker_id: "cb2",
    service_name: "Email Service",
    state: "open" as const,
    failure_count: 5,
    failure_threshold: 5,
    success_count: 80,
  },
  {
    breaker_id: "cb3",
    service_name: "Search",
    state: "half_open" as const,
    failure_count: 3,
    failure_threshold: 5,
    success_count: 150,
  },
];

describe("CircuitBreakerCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<CircuitBreakerCard breakers={breakers} appName="App" />);
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("3 breakers");
    expect(container.textContent).toContain("1 open");
  });

  it("shows service names", () => {
    const { container } = render(<CircuitBreakerCard breakers={breakers} appName="App" />);
    expect(container.textContent).toContain("Payment API");
    expect(container.textContent).toContain("Email Service");
  });

  it("shows state badges", () => {
    const { container } = render(<CircuitBreakerCard breakers={breakers} appName="App" />);
    expect(container.textContent).toContain("closed");
    expect(container.textContent).toContain("open");
    expect(container.textContent).toContain("half open");
  });

  it("shows failure and success counts", () => {
    const { container } = render(<CircuitBreakerCard breakers={breakers} appName="App" />);
    expect(container.textContent).toContain("1/5 failures");
    expect(container.textContent).toContain("200 successes");
  });

  it("shows empty state", () => {
    const { container } = render(<CircuitBreakerCard breakers={[]} appName="App" />);
    expect(container.textContent).toContain("No circuit breakers");
  });
});
