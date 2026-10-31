import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWorkspaceMgrV9Panel } from "@/components/fleet-workspace-mgr-v9-panel";
describe("FleetWorkspaceMgrV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWorkspaceMgrV9Panel total={50} running={30} />);
    expect(container.textContent).toContain("Workspace Manager v9");
}); });
