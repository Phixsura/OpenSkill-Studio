import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TopoChangeViewer } from "@/components/topo-change-viewer";

describe("TopoChangeViewer", () => {
  it("renders", () => {
    const { container } = render(
      <TopoChangeViewer totalChanges={4} breaking={true}
        servicesAdded={["queue"]} servicesRemoved={["cache"]}
        connectionsAdded={["api→queue"]} connectionsRemoved={["api→cache"]} />
    );
    expect(container.textContent).toContain("Topology Changes");
    expect(container.textContent).toContain("4 changes");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("+ service: queue");
    expect(container.textContent).toContain("- service: cache");
  });
});
