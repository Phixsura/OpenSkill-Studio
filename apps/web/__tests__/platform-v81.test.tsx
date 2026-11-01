import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV81 } from "@/components/platform-v81";
describe("PlatformV81", () => { it("renders", () => {
    const { container } = render(<PlatformV81 />);
    expect(container.textContent).toContain("v81");
}); });
