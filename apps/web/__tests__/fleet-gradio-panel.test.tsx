import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGradioPanel } from "@/components/fleet-gradio-panel";
describe("FleetGradioPanel", () => { it("renders", () => {
    const { container } = render(<FleetGradioPanel apps={10} running={10} interfaces={30} users={50000} />);
    expect(container.textContent).toContain("Gradio");
}); });
