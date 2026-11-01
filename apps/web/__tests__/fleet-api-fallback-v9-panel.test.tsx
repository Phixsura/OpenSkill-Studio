import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiFallbackV9Panel } from "@/components/fleet-api-fallback-v9-panel";
describe("FleetApiFallbackV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiFallbackV9Panel fallbacks={30} triggered={5} />);
    expect(container.textContent).toContain("API Fallback v9");
}); });
