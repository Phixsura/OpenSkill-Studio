import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetJupyterhubPanel } from "@/components/fleet-jupyterhub-panel";
describe("FleetJupyterhubPanel", () => { it("renders", () => {
    const { container } = render(<FleetJupyterhubPanel hubs={3} running={3} activeUsers={1500} servers={1500} />);
    expect(container.textContent).toContain("JupyterHub");
}); });
