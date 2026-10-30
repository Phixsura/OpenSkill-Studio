import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-connection-pool-card";

describe("ConsumerApiConnectionPoolCard", () => {
  it("shows pool stats", () => {
    const { container } = render(<Card consumerId="c1" active={5} idle={3} max={20} utilPct={40} idleTimeoutSec={300} appName="App" />);
    expect(container.textContent).toContain("Connection Pool");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("20");
    expect(container.textContent).toContain("40%");
    expect(container.textContent).toContain("300s");
  });
  it("shows high utilization", () => {
    const { container } = render(<Card consumerId="c1" active={9} idle={1} max={10} utilPct={100} idleTimeoutSec={60} appName="App" />);
    expect(container.textContent).toContain("100%");
  });
});
