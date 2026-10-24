import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiResponseHeaderV9Panel } from "@/components/fleet-api-response-header-v9-panel";
describe("FleetApiResponseHeaderV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiResponseHeaderV9Panel endpoints={200} hsts={200} />);
    expect(container.textContent).toContain("Response Header v9");
}); });
