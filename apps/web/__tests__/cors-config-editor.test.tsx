import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CorsConfigEditor } from "@/components/cors-config-editor";

describe("CorsConfigEditor", () => {
  it("renders and removes", () => {
    const onRemove = vi.fn();
    const { container, getAllByText } = render(
      <CorsConfigEditor origins={["https://app.example.com"]} methods={["GET", "POST"]}
        headers={["Content-Type"]} credentials={true}
        onAddOrigin={vi.fn()} onRemoveOrigin={onRemove} />
    );
    expect(container.textContent).toContain("CORS Policy");
    expect(container.textContent).toContain("https://app.example.com");
    expect(container.textContent).toContain("GET, POST");
    fireEvent.click(getAllByText("×")[0]);
    expect(onRemove).toHaveBeenCalledWith("https://app.example.com");
  });
});
