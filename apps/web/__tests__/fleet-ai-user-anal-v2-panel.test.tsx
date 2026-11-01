import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiUserAnalV2Panel } from "@/components/fleet-ai-user-anal-v2-panel";
describe("FleetAiUserAnalV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiUserAnalV2Panel dashboards={3} active={3} dau={2000000} mau={8000000} retention={90} engagement={30} />);
    expect(container.textContent).toContain("User Analytics v2");
}); });
