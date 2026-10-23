import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUmaintenanceUbanner } from "@/components/platform-maintenance-banner";

describe("UplatformUmaintenanceUbanner", () => {
  it("renders", () => {
    const { container } = render(<UplatformUmaintenanceUbanner status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});
