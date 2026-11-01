import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCorsV9Panel } from "@/components/fleet-api-cors-v9-panel";
describe("FleetApiCorsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCorsV9Panel policies={50} wildcard={0} />);
    expect(container.textContent).toContain("API CORS v9");
}); });
