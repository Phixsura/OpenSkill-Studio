import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUstatusUindicator } from "@/components/platform-status-indicator";

describe("UplatformUstatusUindicator", () => {
  it("renders", () => {
    const { container } = render(<UplatformUstatusUindicator status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});
