import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRetentionV7Panel } from "@/components/fleet-ai-retention-v7-panel";
describe("FleetAiRetentionV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiRetentionV7Panel trackers={3} active={3} d1={85} d7={70} d30={60} d90={50} />);
    expect(container.textContent).toContain("Retention v7");
}); });
