import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSpecV9Panel } from "@/components/fleet-api-spec-v9-panel";
describe("FleetApiSpecV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSpecV9Panel specs={30} valid={30} />);
    expect(container.textContent).toContain("API Spec v9");
}); });
