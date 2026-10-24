import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStreamlitPanel } from "@/components/fleet-streamlit-panel";
describe("FleetStreamlitPanel", () => { it("renders", () => {
    const { container } = render(<FleetStreamlitPanel apps={15} deployed={15} viewers={100000} components={200} />);
    expect(container.textContent).toContain("Streamlit");
}); });
