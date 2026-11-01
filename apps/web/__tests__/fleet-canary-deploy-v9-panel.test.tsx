import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCanaryDeployV9Panel } from "@/components/fleet-canary-deploy-v9-panel";
describe("FleetCanaryDeployV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCanaryDeployV9Panel total={10} promoted={8} />);
    expect(container.textContent).toContain("Canary Deploy v9");
}); });
