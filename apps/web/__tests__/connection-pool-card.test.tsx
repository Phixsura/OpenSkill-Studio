import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ConnectionPoolCard from "../src/components/connection-pool-card";

const pools = [
  {
    pool_id: "main-db",
    max_size: 20,
    active: 15,
    idle: 5,
    waiting: 0,
    utilization_pct: 75,
    avg_acquire_ms: 12,
    saturated: false,
  },
  {
    pool_id: "read-replica",
    max_size: 10,
    active: 10,
    idle: 0,
    waiting: 3,
    utilization_pct: 100,
    avg_acquire_ms: 45,
    saturated: true,
  },
];

describe("ConnectionPoolCard", () => {
  it("renders header", () => {
    const { container } = render(<ConnectionPoolCard pools={pools} appName="My App" />);
    expect(container.textContent).toContain("Connection Pools");
  });

  it("shows saturated badge", () => {
    const { container } = render(<ConnectionPoolCard pools={pools} appName="App" />);
    expect(container.textContent).toContain("1 saturated");
  });

  it("shows healthy when none saturated", () => {
    const { container } = render(<ConnectionPoolCard pools={[pools[0]]} appName="App" />);
    expect(container.textContent).toContain("Healthy");
  });

  it("renders pool ids", () => {
    const { container } = render(<ConnectionPoolCard pools={pools} appName="App" />);
    expect(container.textContent).toContain("main-db");
    expect(container.textContent).toContain("read-replica");
  });

  it("shows active/idle/waiting", () => {
    const { container } = render(<ConnectionPoolCard pools={pools} appName="App" />);
    expect(container.textContent).toContain("15 active");
    expect(container.textContent).toContain("3 waiting");
  });

  it("shows acquire time", () => {
    const { container } = render(<ConnectionPoolCard pools={pools} appName="App" />);
    expect(container.textContent).toContain("12ms acquire");
  });

  it("shows empty state", () => {
    const { container } = render(<ConnectionPoolCard pools={[]} appName="App" />);
    expect(container.textContent).toContain("No connection pools");
  });
});
