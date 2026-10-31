import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV38 } from "@/components/platform-v38";
describe("PlatformV38", () => { it("renders", () => {
    const { container } = render(<PlatformV38 />);
    expect(container.textContent).toContain("v38");
    expect(container.textContent).toContain("317K");
}); });
