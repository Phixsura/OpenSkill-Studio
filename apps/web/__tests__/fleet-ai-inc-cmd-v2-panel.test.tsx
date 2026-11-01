import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIncCmdV2Panel } from "@/components/fleet-ai-inc-cmd-v2-panel";
describe("FleetAiIncCmdV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiIncCmdV2Panel commanders={3} active={3} incidents={500} mttr={5} autoRemediated={480} />);
    expect(container.textContent).toContain("Incident Commander v2");
}); });
