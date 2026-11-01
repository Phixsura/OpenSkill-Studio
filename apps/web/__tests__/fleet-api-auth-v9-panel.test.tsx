import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiAuthV9Panel } from "@/components/fleet-api-auth-v9-panel";
describe("FleetApiAuthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiAuthV9Panel endpoints={100} jwt={80} />);
    expect(container.textContent).toContain("API Auth v9");
}); });
