import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiPlatformMaturityV9Panel } from "@/components/fleet-api-platform-maturity-v9-panel";
describe("FleetApiPlatformMaturityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiPlatformMaturityV9Panel />);
    expect(container.textContent).toContain("Platform Maturity v9");
}); });
