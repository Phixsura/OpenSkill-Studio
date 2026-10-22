import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstalledAppCard } from "@/components/installed-app-card";

describe("InstalledAppCard", () => {
  it("shows app info", () => {
    const { container } = render(<InstalledAppCard appName="My App" category="connector" version="2.0" status="active" healthScore={95} healthStatus="healthy" installedAt="Jan 2026" />);
    expect(container.textContent).toContain("My App");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("95%");
  });
});
