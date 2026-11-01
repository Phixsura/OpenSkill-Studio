import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiConvSumPanel } from "@/components/fleet-ai-conv-sum-panel";
describe("FleetAiConvSumPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiConvSumPanel summarizers={3} active={3} summarized={10000000} compression={8} retention={97} />);
    expect(container.textContent).toContain("Conversation Summarizer");
}); });
