import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSdkPanel } from "@/components/fleet-ai-sdk-panel";
describe("FleetAiSdkPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSdkPanel sdks={5} languages={5} downloads={1000000} activeUsers={100000} />);
    expect(container.textContent).toContain("AI SDK");
}); });
