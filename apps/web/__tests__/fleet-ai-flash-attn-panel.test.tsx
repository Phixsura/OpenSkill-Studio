import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFlashAttnPanel } from "@/components/fleet-ai-flash-attn-panel";
describe("FleetAiFlashAttnPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFlashAttnPanel implementations={4} active={4} speedup={4} memorySaved={65} maxSeqLen={2000000} />);
    expect(container.textContent).toContain("Flash Attention");
}); });
