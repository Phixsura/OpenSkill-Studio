import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLabelstudioPanel } from "@/components/fleet-labelstudio-panel";
describe("FleetLabelstudioPanel", () => { it("renders", () => {
    const { container } = render(<FleetLabelstudioPanel instances={3} running={3} projects={60} annotations={1000000} />);
    expect(container.textContent).toContain("Label Studio");
}); });
