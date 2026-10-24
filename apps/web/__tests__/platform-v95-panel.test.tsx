import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV95Panel } from "@/components/platform-v95-panel";
describe("PlatformV95Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV95Panel />);
    expect(container.textContent).toContain("v95");
    expect(container.textContent).toContain("v100");
}); });
