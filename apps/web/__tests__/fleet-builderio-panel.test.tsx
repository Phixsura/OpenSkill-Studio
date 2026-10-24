import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBuilderioPanel } from "@/components/fleet-builderio-panel";
describe("FleetBuilderioPanel", () => { it("renders", () => {
    const { container } = render(<FleetBuilderioPanel spaces={3} active={3} pages={1000} components={200} />);
    expect(container.textContent).toContain("Builder.io");
}); });
