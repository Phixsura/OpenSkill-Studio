import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiPlaygroundV9Panel } from "@/components/fleet-api-playground-v9-panel";
describe("FleetApiPlaygroundV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiPlaygroundV9Panel playgrounds={10} users={100} />);
    expect(container.textContent).toContain("API Playground v9");
}); });
