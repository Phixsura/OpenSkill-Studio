import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatMigV2Panel } from "@/components/fleet-ai-plat-mig-v2-panel";
describe("FleetAiPlatMigV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatMigV2Panel migrations={5} running={1} completed={4} dataTb={2000} zeroDowntime={true} />);
    expect(container.textContent).toContain("Migration v2");
}); });
