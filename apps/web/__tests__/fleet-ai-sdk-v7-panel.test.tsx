import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSdkV7Panel } from "@/components/fleet-ai-sdk-v7-panel";
describe("FleetAiSdkV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSdkV7Panel sdks={5} active={5} languages={10} downloads={20000000} stars={100000} />);
    expect(container.textContent).toContain("AI SDK v7");
}); });
