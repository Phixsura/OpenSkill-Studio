import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SecretManagerPanel } from "@/components/secret-manager-panel";

const mockSecrets = [
  { name: "DB_PASSWORD", scope: "sandbox", version: 3, accessCount: 42 },
  { name: "API_KEY", scope: "extension", version: 1, accessCount: 100 },
];

describe("SecretManagerPanel", () => {
  it("renders secrets", () => {
    const { container } = render(<SecretManagerPanel secrets={mockSecrets} />);
    expect(container.textContent).toContain("DB_PASSWORD");
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("accessed 42x");
  });

  it("calls onRotate", () => {
    const onRotate = vi.fn();
    const { getAllByText } = render(<SecretManagerPanel secrets={mockSecrets} onRotate={onRotate} />);
    fireEvent.click(getAllByText("Rotate")[0]);
    expect(onRotate).toHaveBeenCalledWith("DB_PASSWORD");
  });

  it("opens add form", () => {
    const { getByText, getByPlaceholderText } = render(
      <SecretManagerPanel secrets={[]} />
    );
    fireEvent.click(getByText("+ Add Secret"));
    expect(getByPlaceholderText("SECRET_NAME")).toBeDefined();
  });

  it("calls onStore", () => {
    const onStore = vi.fn();
    const { getByText, getByPlaceholderText } = render(
      <SecretManagerPanel secrets={[]} onStore={onStore} />
    );
    fireEvent.click(getByText("+ Add Secret"));
    fireEvent.change(getByPlaceholderText("SECRET_NAME"), { target: { value: "NEW_KEY" } });
    fireEvent.change(getByPlaceholderText("Secret value"), { target: { value: "secret123" } });
    fireEvent.click(getByText("Store"));
    expect(onStore).toHaveBeenCalledWith("NEW_KEY", "secret123", "sandbox");
  });
});
