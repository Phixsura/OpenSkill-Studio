import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInfraV7Panel } from "@/components/fleet-ai-infra-v7-panel";
describe("FleetAiInfraV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiInfraV7Panel systems={5} active={5} clusters={200} nodes={20000} gpus={100000} storage={1000} />);
    expect(container.textContent).toContain("Infrastructure v7");
}); });
