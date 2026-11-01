import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiOpenapiV9Panel } from "@/components/fleet-api-openapi-v9-panel";
describe("FleetApiOpenapiV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiOpenapiV9Panel specs={30} errors={0} />);
    expect(container.textContent).toContain("API OpenAPI v9");
}); });
