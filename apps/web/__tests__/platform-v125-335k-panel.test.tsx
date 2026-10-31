import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV125335kPanel } from "@/components/platform-v125-335k-panel";
describe("PlatformV125335kPanel", () => { it("renders", () => {
    const { container } = render(<PlatformV125335kPanel />);
    expect(container.textContent).toContain("v125");
    expect(container.textContent).toContain("335K");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
