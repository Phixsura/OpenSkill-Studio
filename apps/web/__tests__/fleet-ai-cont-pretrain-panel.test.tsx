import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiContPretrainPanel } from "@/components/fleet-ai-cont-pretrain-panel";
describe("FleetAiContPretrainPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiContPretrainPanel jobs={3} active={3} tokens={30000000000000} loss={1.3} gpus={4096} />);
    expect(container.textContent).toContain("Continuous Pretraining");
}); });
