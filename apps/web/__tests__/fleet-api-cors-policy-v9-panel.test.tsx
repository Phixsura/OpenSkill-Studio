import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCorsPolicyV9Panel } from "@/components/fleet-api-cors-policy-v9-panel";
describe("FleetApiCorsPolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCorsPolicyV9Panel policies={20} strict={20} />);
    expect(container.textContent).toContain("CORS Policy v9");
}); });
