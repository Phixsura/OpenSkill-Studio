import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTransferPanel } from "@/components/fleet-ai-transfer-panel";
describe("FleetAiTransferPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTransferPanel jobs={8} active={8} baseModels={5} adaptations={40} improvement={30} />);
    expect(container.textContent).toContain("Transfer Learning");
}); });
