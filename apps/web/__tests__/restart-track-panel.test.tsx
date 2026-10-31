import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RestartTrackPanel } from "@/components/restart-track-panel";
describe("RestartTrackPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RestartTrackPanel totalRestarts={5} crashLoops={1}
        services={[
          { service: "api", restarts: 4, crashLoop: true, lastReason: "OOM" },
          { service: "worker", restarts: 1, crashLoop: false, lastReason: "signal" },
        ]} />
    );
    expect(container.textContent).toContain("Restart Tracker");
    expect(container.textContent).toContain("5 restarts");
    expect(container.textContent).toContain("1 crash loops");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("OOM");
    expect(container.textContent).toContain("4x");
  });
});
