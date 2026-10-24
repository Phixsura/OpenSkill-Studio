import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV66 } from "@/components/platform-v66";
describe("PlatformV66", () => { it("renders", () => {
    const { container } = render(<PlatformV66 />);
    expect(container.textContent).toContain("v66");
}); });
