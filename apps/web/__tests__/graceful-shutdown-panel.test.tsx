import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GracefulShutdownPanel } from "@/components/graceful-shutdown-panel";

describe("GracefulShutdownPanel", () => {
  it("renders draining state with batches", () => {
    const { container } = render(
      <GracefulShutdownPanel state="draining" activeConnections={5} drainSeconds={30}
        batches={[
          { batch: 1, instances: ["i1", "i2"], size: 2 },
          { batch: 2, instances: ["i3"], size: 1 },
        ]} />
    );
    expect(container.textContent).toContain("Graceful Shutdown");
    expect(container.textContent).toContain("draining");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("30s");
    expect(container.textContent).toContain("Batch 1");
    expect(container.textContent).toContain("i1, i2");
  });
});
