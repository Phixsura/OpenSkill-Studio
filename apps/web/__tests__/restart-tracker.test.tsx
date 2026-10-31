import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RestartTracker } from "@/components/restart-tracker";

describe("RestartTracker", () => {
  it("renders", () => {
    const { container } = render(
      <RestartTracker crashLoopCount={1} allStable={false} services={[
        { service: "api", restarts: 0, ratePerHour: 0, crashLoop: false },
        { service: "worker", restarts: 10, ratePerHour: 20, crashLoop: true },
      ]} />
    );
    expect(container.textContent).toContain("Restart Tracker");
    expect(container.textContent).toContain("1 crash-looping");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("worker");
    expect(container.textContent).toContain("10 restarts");
  });
});
