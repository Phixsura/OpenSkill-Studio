import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLoraPanel } from "@/components/fleet-ai-lora-panel";
describe("FleetAiLoraPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLoraPanel adapters={10} active={10} rank={128} trained={500} paramPct={0.05} />);
    expect(container.textContent).toContain("LoRA Adapter");
}); });
