import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUuptimeUwidget } from "@/components/platform-uptime-widget";

describe("UplatformUuptimeUwidget", () => {
  it("renders", () => {
    const { container } = render(<UplatformUuptimeUwidget status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});
