import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiContentFltPanel } from "@/components/fleet-ai-content-flt-panel";
describe("FleetAiContentFltPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiContentFltPanel filters={5} active={5} scanned={50000000} blocked={25000} blockRate={0.05} />);
    expect(container.textContent).toContain("Content Filter");
}); });
