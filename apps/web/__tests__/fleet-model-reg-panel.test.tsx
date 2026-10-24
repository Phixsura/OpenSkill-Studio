import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetModelRegPanel } from "@/components/fleet-model-reg-panel";
describe("FleetModelRegPanel", () => { it("renders", () => {
    const { container } = render(<FleetModelRegPanel registries={5} models={200} versions={1000} deployed={400} deploymentRate={40} />);
    expect(container.textContent).toContain("Model Registry");
}); });
