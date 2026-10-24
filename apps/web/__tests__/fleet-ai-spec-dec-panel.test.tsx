import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSpecDecPanel } from "@/components/fleet-ai-spec-dec-panel";
describe("FleetAiSpecDecPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSpecDecPanel decoders={4} active={4} tokens={50000000000} acceptanceRate={82} speedup={3.2} />);
    expect(container.textContent).toContain("Speculative Decoding");
}); });
