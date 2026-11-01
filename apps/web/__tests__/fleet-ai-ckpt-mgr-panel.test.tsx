import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCkptMgrPanel } from "@/components/fleet-ai-ckpt-mgr-panel";
describe("FleetAiCkptMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCkptMgrPanel managers={3} active={3} checkpoints={10000} storageTb={200} autoCleanup={true} />);
    expect(container.textContent).toContain("Checkpoint");
}); });
