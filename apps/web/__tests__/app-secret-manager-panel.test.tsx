import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppSecretManagerPanel } from "@/components/app-secret-manager-panel";

const MOCK_SECRETS = [
  {
    key: "API_KEY",
    version: 3,
    created_at: "2026-10-01T00:00:00Z",
    updated_at: "2026-10-25T00:00:00Z",
    expires_at: null,
    has_previous: false,
    value_hash: "a1b2c3d4e5f6g7h8",
  },
  {
    key: "DB_PASSWORD",
    version: 1,
    created_at: "2026-10-20T00:00:00Z",
    updated_at: "2026-10-20T00:00:00Z",
    expires_at: "2027-01-20T00:00:00Z",
    has_previous: true,
    value_hash: "ff00ee11dd22cc33",
  },
];

const defaultProps = {
  installationId: "inst-1",
  secrets: MOCK_SECRETS,
  maxSecrets: 50,
  onAdd: vi.fn(),
  onRotate: vi.fn(),
  onDelete: vi.fn(),
};

describe("AppSecretManagerPanel", () => {
  it("renders heading and count", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("Secrets");
    expect(container.textContent).toContain("2/50");
  });

  it("renders secret keys", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("API_KEY");
    expect(container.textContent).toContain("DB_PASSWORD");
  });

  it("renders version badges", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("v1");
  });

  it("shows rotating badge for secrets with previous value", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("rotating");
  });

  it("shows expiry date", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("expires");
  });

  it("shows hash prefix", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} />);
    expect(container.textContent).toContain("a1b2c3d4e5f6g7h8");
  });

  it("shows empty state", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} secrets={[]} />);
    expect(container.textContent).toContain("No secrets stored");
  });

  it("shows Add Secret button", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} />);
    const btn = Array.from(container.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Add Secret"),
    );
    expect(btn).toBeTruthy();
  });

  it("shows add form on click", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} />);
    const btn = Array.from(container.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Add Secret"),
    )!;
    fireEvent.click(btn);
    expect(container.querySelector("input[aria-label='Secret key']")).toBeTruthy();
    expect(container.querySelector("input[aria-label='Secret value']")).toBeTruthy();
  });

  it("calls onAdd when form submitted", () => {
    const onAdd = vi.fn();
    const { container } = render(<AppSecretManagerPanel {...defaultProps} onAdd={onAdd} />);
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) =>
        b.textContent?.includes("Add Secret"),
      )!,
    );
    const keyInput = container.querySelector("input[aria-label='Secret key']") as HTMLInputElement;
    const valInput = container.querySelector(
      "input[aria-label='Secret value']",
    ) as HTMLInputElement;
    fireEvent.change(keyInput, { target: { value: "NEW_KEY" } });
    fireEvent.change(valInput, { target: { value: "new-secret" } });
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find(
        (b) => b.textContent === "Save Secret",
      )!,
    );
    expect(onAdd).toHaveBeenCalledWith("NEW_KEY", "new-secret");
  });

  it("calls onRotate", () => {
    const onRotate = vi.fn();
    const { container } = render(<AppSecretManagerPanel {...defaultProps} onRotate={onRotate} />);
    const rotateBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Rotate",
    );
    fireEvent.click(rotateBtns[0]);
    expect(onRotate).toHaveBeenCalledWith("API_KEY");
  });

  it("calls onDelete", () => {
    const onDelete = vi.fn();
    const { container } = render(<AppSecretManagerPanel {...defaultProps} onDelete={onDelete} />);
    const deleteBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Delete",
    );
    fireEvent.click(deleteBtns[0]);
    expect(onDelete).toHaveBeenCalledWith("API_KEY");
  });

  it("shows limit reached when at max", () => {
    const { container } = render(<AppSecretManagerPanel {...defaultProps} maxSecrets={2} />);
    expect(container.textContent).toContain("Limit reached");
    const addBtn = Array.from(container.querySelectorAll("button")).find((b) =>
      b.textContent?.includes("Add Secret"),
    );
    expect(addBtn).toBeFalsy();
  });
});
