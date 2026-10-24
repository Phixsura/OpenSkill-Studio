import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV73 } from "@/components/platform-v73";
describe("PlatformV73", () => { it("renders", () => {
    const { container } = render(<PlatformV73 />);
    expect(container.textContent).toContain("v73");
    expect(container.textContent).toContain("324K");
}); });
