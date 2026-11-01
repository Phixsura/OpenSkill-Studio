import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatformValueV7Panel } from "@/components/fleet-ai-platform-value-v7-panel";
describe("FleetAiPlatformValueV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatformValueV7Panel trackers={3} active={3} value={20000000000} roi={600} hours={50000000} />);
    expect(container.textContent).toContain("Platform Value v7");
}); });
