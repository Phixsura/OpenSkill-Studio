import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGradCkptPanel } from "@/components/fleet-ai-grad-ckpt-panel";
describe("FleetAiGradCkptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGradCkptPanel managers={4} active={4} savedGb={2000} overhead={12} jobs={100} />);
    expect(container.textContent).toContain("Gradient Checkpoint");
}); });
