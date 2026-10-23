import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvVarEditor } from "@/components/env-var-editor";

describe("EnvVarEditor", () => {
  it("renders vars and adds", () => {
    const onAdd = vi.fn();
    const { container, getByPlaceholderText, getByText } = render(
      <EnvVarEditor vars={[
        { key: "DB_URL", masked: "po****db", sensitive: true },
        { key: "APP_ENV", masked: "production", sensitive: false },
      ]} onAdd={onAdd} />
    );
    expect(container.textContent).toContain("Environment Variables");
    expect(container.textContent).toContain("DB_URL");
    expect(container.textContent).toContain("po****db");
    fireEvent.change(getByPlaceholderText("KEY"), { target: { value: "NEW_KEY" } });
    fireEvent.change(getByPlaceholderText("value"), { target: { value: "secret" } });
    fireEvent.click(getByText("Add"));
    expect(onAdd).toHaveBeenCalledWith("NEW_KEY", "secret", true);
  });
});
