import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionMarketplaceBrowser } from "@/components/extension-marketplace-browser";

const mockExtensions = [
  { id: "1", name: "Code Formatter", author: "Alice", version: "1.0.0",
    description: "Auto-format code", downloads: 5000, rating: 4.5, installed: false },
  { id: "2", name: "Theme Dark", author: "Bob", version: "2.1.0",
    description: "Dark theme pack", downloads: 12000, rating: 4.8, installed: true },
  { id: "3", name: "Linter Pro", author: "Alice", version: "3.0.0",
    description: "Advanced linting", downloads: 8000, rating: 4.2, installed: false },
];

describe("ExtensionMarketplaceBrowser", () => {
  it("renders all extensions", () => {
    const { container } = render(<ExtensionMarketplaceBrowser extensions={mockExtensions} />);
    expect(container.textContent).toContain("Code Formatter");
    expect(container.textContent).toContain("Theme Dark");
    expect(container.textContent).toContain("Linter Pro");
    expect(container.textContent).toContain("3 extensions found");
  });

  it("filters by search", () => {
    const { container, getByPlaceholderText } = render(
      <ExtensionMarketplaceBrowser extensions={mockExtensions} />
    );
    fireEvent.change(getByPlaceholderText("Search extensions..."), { target: { value: "dark" } });
    expect(container.textContent).toContain("1 extensions found");
    expect(container.textContent).toContain("Theme Dark");
  });

  it("shows install/uninstall buttons", () => {
    const onInstall = vi.fn();
    const { getAllByText } = render(
      <ExtensionMarketplaceBrowser extensions={mockExtensions} onInstall={onInstall} />
    );
    const installBtns = getAllByText("Install");
    expect(installBtns.length).toBe(2);
    fireEvent.click(installBtns[0]);
    expect(onInstall).toHaveBeenCalledWith("1");
  });
});
