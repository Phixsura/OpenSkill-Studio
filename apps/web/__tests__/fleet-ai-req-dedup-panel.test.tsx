import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiReqDedupPanel } from "@/components/fleet-ai-req-dedup-panel";
describe("FleetAiReqDedupPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiReqDedupPanel dedupers={4} active={4} requests={50000000} deduped={10000000} savings={20} />);
    expect(container.textContent).toContain("Request Dedup");
}); });
