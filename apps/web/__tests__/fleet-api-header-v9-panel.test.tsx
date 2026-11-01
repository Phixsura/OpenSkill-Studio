import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiHeaderV9Panel } from "@/components/fleet-api-header-v9-panel";
describe("FleetApiHeaderV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiHeaderV9Panel policies={20} security={10} />);
    expect(container.textContent).toContain("API Header v9");
}); });
