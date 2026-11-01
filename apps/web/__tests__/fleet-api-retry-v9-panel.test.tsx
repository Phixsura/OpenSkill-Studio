import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiRetryV9Panel } from "@/components/fleet-api-retry-v9-panel";
describe("FleetApiRetryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiRetryV9Panel endpoints={100} retries={500} />);
    expect(container.textContent).toContain("API Retry v9");
}); });
