import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDevSdkPanel } from "@/components/fleet-ai-dev-sdk-panel";
describe("FleetAiDevSdkPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDevSdkPanel sdks={5} active={5} languages={10} downloads={200000} developers={100000} />);
    expect(container.textContent).toContain("Developer SDK");
}); });
