import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCompositionV9Panel } from "@/components/fleet-api-composition-v9-panel";
describe("FleetApiCompositionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCompositionV9Panel compositions={20} backends={60} />);
    expect(container.textContent).toContain("API Composition v9");
}); });
