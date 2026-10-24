import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDpoPanel } from "@/components/fleet-ai-dpo-panel";
describe("FleetAiDpoPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDpoPanel trainers={3} active={3} pairs={2000000} epochs={5} winRate={78} />);
    expect(container.textContent).toContain("DPO Training");
}); });
