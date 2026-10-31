import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWarmPoolPanel } from "@/components/fleet-ai-warm-pool-panel";
describe("FleetAiWarmPoolPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWarmPoolPanel pools={4} active={4} warm={100} prevented={500000} overhead={10} />);
    expect(container.textContent).toContain("Warm Pool");
}); });
