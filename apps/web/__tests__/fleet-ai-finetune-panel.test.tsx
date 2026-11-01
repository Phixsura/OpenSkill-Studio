import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFinetunPanel } from "@/components/fleet-ai-finetune-panel";
describe("FleetAiFinetunPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFinetunPanel jobs={10} running={2} completed={7} failed={1} epochs={100} />);
    expect(container.textContent).toContain("AI Fine-Tuning");
}); });
