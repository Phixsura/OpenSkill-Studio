import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetThreadsPanel } from "@/components/fleet-threads-panel";
describe("FleetThreadsPanel", () => { it("renders", () => {
    const { container } = render(<FleetThreadsPanel active={370} max={400} pct={92.5} exhausted={true} />);
    expect(container.textContent).toContain("Fleet Threads");
    expect(container.textContent).toContain("370/400");
}); });
