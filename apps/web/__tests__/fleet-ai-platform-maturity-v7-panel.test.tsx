import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatformMaturityV7Panel } from "@/components/fleet-ai-platform-maturity-v7-panel";
describe("FleetAiPlatformMaturityV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatformMaturityV7Panel assessors={3} active={3} level={5} dimensions={50} score={99} />);
    expect(container.textContent).toContain("Platform Maturity v7");
}); });
