import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatformFutureV7Panel } from "@/components/fleet-ai-platform-future-v7-panel";
describe("FleetAiPlatformFutureV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatformFutureV7Panel planners={3} active={3} capabilities={200} research={100} prototypes={50} />);
    expect(container.textContent).toContain("Platform Future v7");
}); });
