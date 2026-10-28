import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ThrottleControllerCard from "../src/components/throttle-controller-card";

const lowState = {
  load_level: "low" as const,
  current_load: 0.3,
  allowed_rps: 1000,
  max_rps: 1000,
  throttle_pct: 100,
};
const highState = {
  load_level: "high" as const,
  current_load: 0.9,
  allowed_rps: 500,
  max_rps: 1000,
  throttle_pct: 50,
};
const criticalState = {
  load_level: "critical" as const,
  current_load: 0.97,
  allowed_rps: 100,
  max_rps: 1000,
  throttle_pct: 10,
};

describe("ThrottleControllerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ThrottleControllerCard state={lowState} appName="My App" />);
    expect(container.textContent).toContain("Throttle Control");
    expect(container.textContent).toContain("My App");
  });

  it("shows load level badge", () => {
    const { container } = render(<ThrottleControllerCard state={highState} appName="App" />);
    expect(container.textContent).toContain("High");
  });

  it("shows load percentage", () => {
    const { container } = render(<ThrottleControllerCard state={highState} appName="App" />);
    expect(container.textContent).toContain("90%");
  });

  it("shows allowed RPS", () => {
    const { container } = render(<ThrottleControllerCard state={highState} appName="App" />);
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("Allowed RPS");
  });

  it("shows max RPS", () => {
    const { container } = render(<ThrottleControllerCard state={lowState} appName="App" />);
    expect(container.textContent).toContain("1000");
    expect(container.textContent).toContain("Max RPS");
  });

  it("shows throughput percentage", () => {
    const { container } = render(<ThrottleControllerCard state={criticalState} appName="App" />);
    expect(container.textContent).toContain("10%");
    expect(container.textContent).toContain("Throughput");
  });

  it("shows critical badge", () => {
    const { container } = render(<ThrottleControllerCard state={criticalState} appName="App" />);
    expect(container.textContent).toContain("Critical");
  });
});
