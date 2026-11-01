import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTokenCntPanel } from "@/components/fleet-ai-token-cnt-panel";
describe("FleetAiTokenCntPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTokenCntPanel accounts={20} inputTokens={5000000000} outputTokens={2000000000} totalCost={50000} />);
    expect(container.textContent).toContain("Token Counter");
}); });
