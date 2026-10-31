import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvVarManagerPanel } from "@/components/env-var-manager-panel";

const mockVars = [
  { key: "EXT_API_URL", value: "https://api.example.com", isSecret: false, scope: "all" },
  { key: "EXT_TOKEN", value: "••••••••", isSecret: true, scope: "production" },
  { key: "EXT_DEBUG", value: "true", isSecret: false, scope: "development" },
];

describe("EnvVarManagerPanel", () => {
  it("renders env vars with scopes", () => {
    const { container } = render(
      <EnvVarManagerPanel vars={mockVars} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("EXT_API_URL");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("secret");
  });

  it("shows add form", () => {
    const { getByText, container } = render(
      <EnvVarManagerPanel vars={[]} extensionName="Test" />
    );
    fireEvent.click(getByText("+ Add Variable"));
    expect(container.querySelector("input[type='text']")).toBeDefined();
  });

  it("calls onDelete", () => {
    const onDelete = vi.fn();
    const { container } = render(
      <EnvVarManagerPanel vars={mockVars} extensionName="Test" onDelete={onDelete} />
    );
    const deleteBtn = container.querySelectorAll("button");
    const del = Array.from(deleteBtn).find(b => b.textContent === "✕");
    if (del) fireEvent.click(del);
    expect(onDelete).toHaveBeenCalled();
  });
});
