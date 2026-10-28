import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CircuitBreakerCard from "../src/components/circuit-breaker-card";

const closedBreaker = {
  service: "auth-api",
  state: "closed" as const,
  failure_count: 1,
  failure_threshold: 5,
  success_count: 0,
  success_threshold: 2,
  last_failure_at: new Date(Date.now() - 120_000).toISOString(),
  opened_at: null,
  recovery_timeout_seconds: 30,
};

const openBreaker = {
  service: "payment-svc",
  state: "open" as const,
  failure_count: 5,
  failure_threshold: 5,
  success_count: 0,
  success_threshold: 2,
  last_failure_at: new Date(Date.now() - 10_000).toISOString(),
  opened_at: new Date(Date.now() - 10_000).toISOString(),
  recovery_timeout_seconds: 60,
};

const halfOpenBreaker = {
  service: "email-svc",
  state: "half_open" as const,
  failure_count: 0,
  failure_threshold: 5,
  success_count: 1,
  success_threshold: 3,
  last_failure_at: new Date(Date.now() - 60_000).toISOString(),
  opened_at: new Date(Date.now() - 45_000).toISOString(),
  recovery_timeout_seconds: 30,
};

describe("CircuitBreakerCard", () => {
  it("renders app name and header", () => {
    const { container } = render(
      <CircuitBreakerCard breakers={[closedBreaker]} appName="My App" />,
    );
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("My App");
  });

  it("shows all-healthy badge when everything is closed", () => {
    const { container } = render(<CircuitBreakerCard breakers={[closedBreaker]} appName="App" />);
    expect(container.textContent).toContain("All healthy");
  });

  it("shows open count badge", () => {
    const { container } = render(
      <CircuitBreakerCard breakers={[openBreaker, closedBreaker]} appName="App" />,
    );
    expect(container.textContent).toContain("1 open");
  });

  it("shows half-open probing badge", () => {
    const { container } = render(<CircuitBreakerCard breakers={[halfOpenBreaker]} appName="App" />);
    expect(container.textContent).toContain("1 probing");
  });

  it("renders service names", () => {
    const { container } = render(
      <CircuitBreakerCard breakers={[closedBreaker, openBreaker]} appName="App" />,
    );
    expect(container.textContent).toContain("auth-api");
    expect(container.textContent).toContain("payment-svc");
  });

  it("renders state labels", () => {
    const { container } = render(
      <CircuitBreakerCard breakers={[closedBreaker, openBreaker, halfOpenBreaker]} appName="App" />,
    );
    expect(container.textContent).toContain("Closed");
    expect(container.textContent).toContain("Open");
    expect(container.textContent).toContain("Half-Open");
  });

  it("renders failure count ratio", () => {
    const { container } = render(<CircuitBreakerCard breakers={[closedBreaker]} appName="App" />);
    expect(container.textContent).toContain("1/5");
  });

  it("shows recovery info for open breaker", () => {
    const { container } = render(<CircuitBreakerCard breakers={[openBreaker]} appName="App" />);
    expect(container.textContent).toContain("recovery in 60s");
  });

  it("shows probe progress for half-open breaker", () => {
    const { container } = render(<CircuitBreakerCard breakers={[halfOpenBreaker]} appName="App" />);
    expect(container.textContent).toContain("1/3 successes");
  });

  it("shows last failure for closed breaker", () => {
    const { container } = render(<CircuitBreakerCard breakers={[closedBreaker]} appName="App" />);
    expect(container.textContent).toContain("Last failure");
  });

  it("shows empty state when no breakers", () => {
    const { container } = render(<CircuitBreakerCard breakers={[]} appName="App" />);
    expect(container.textContent).toContain("No circuit breakers configured");
  });
});
