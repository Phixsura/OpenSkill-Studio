import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import GracefulShutdownCard from "../src/components/graceful-shutdown-card";

const running = {
  phase: "running" as const,
  in_flight_requests: 42,
  drain_timeout_seconds: 30,
  hooks_registered: 3,
  hooks_completed: 0,
  ready_to_shutdown: false,
};
const draining = {
  phase: "draining" as const,
  in_flight_requests: 5,
  drain_timeout_seconds: 30,
  hooks_registered: 3,
  hooks_completed: 2,
  ready_to_shutdown: false,
};
const ready = { ...draining, hooks_completed: 3, in_flight_requests: 0, ready_to_shutdown: true };

describe("GracefulShutdownCard", () => {
  it("renders header", () => {
    const { container } = render(<GracefulShutdownCard state={running} appName="My App" />);
    expect(container.textContent).toContain("Shutdown Status");
  });

  it("shows phase badge", () => {
    const { container } = render(<GracefulShutdownCard state={draining} appName="App" />);
    expect(container.textContent).toContain("Draining");
  });

  it("shows in-flight count", () => {
    const { container } = render(<GracefulShutdownCard state={running} appName="App" />);
    expect(container.textContent).toContain("42");
    expect(container.textContent).toContain("In-flight");
  });

  it("shows hooks progress", () => {
    const { container } = render(<GracefulShutdownCard state={draining} appName="App" />);
    expect(container.textContent).toContain("2/3");
    expect(container.textContent).toContain("Hook progress");
  });

  it("shows ready message", () => {
    const { container } = render(<GracefulShutdownCard state={ready} appName="App" />);
    expect(container.textContent).toContain("Ready to shutdown");
  });

  it("shows timeout", () => {
    const { container } = render(<GracefulShutdownCard state={running} appName="App" />);
    expect(container.textContent).toContain("30s");
    expect(container.textContent).toContain("Timeout");
  });
});
