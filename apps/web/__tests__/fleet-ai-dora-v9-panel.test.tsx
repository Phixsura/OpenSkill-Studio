import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDoraV9Panel } from "@/components/fleet-ai-dora-v9-panel";
describe("FleetAiDoraV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDoraV9Panel />);
    expect(container.textContent).toContain("DORA v9");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
