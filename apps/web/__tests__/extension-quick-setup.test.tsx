import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionQuickSetup } from "@/components/extension-quick-setup";

const mockSteps = [
  { id: "install", title: "Install SDK", command: "npm install @openskill/sdk", description: "Add the SDK to your project" },
  { id: "init", title: "Initialize", command: "npx osk init my-extension", description: "Create extension scaffold" },
  { id: "dev", title: "Start Dev Server", command: "npm run dev", description: "Run in development mode" },
];

describe("ExtensionQuickSetup", () => {
  it("renders steps", () => {
    const { container } = render(
      <ExtensionQuickSetup extensionName="Slack Bot" steps={mockSteps} />
    );
    expect(container.textContent).toContain("Quick Setup");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Install SDK");
    expect(container.textContent).toContain("npm install @openskill/sdk");
  });

  it("navigates steps", () => {
    const { getByText, container } = render(
      <ExtensionQuickSetup extensionName="Test" steps={mockSteps} />
    );
    fireEvent.click(getByText("Next →"));
    // Step 2 should be highlighted now
    expect(container.textContent).toContain("Initialize");
  });

  it("shows package manager", () => {
    const { container } = render(
      <ExtensionQuickSetup extensionName="Test" steps={mockSteps} packageManager="pnpm" />
    );
    expect(container.textContent).toContain("pnpm install @openskill/sdk");
  });
});
