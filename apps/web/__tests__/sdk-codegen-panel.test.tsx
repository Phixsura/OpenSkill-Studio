import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SdkCodegenPanel } from "@/components/sdk-codegen-panel";

describe("SdkCodegenPanel", () => {
  it("shows code", () => {
    const code = { typescript: "class Client {}", python: "class Client: pass" };
    const { container } = render(<SdkCodegenPanel generatedCode={code} languages={["typescript", "python"]} />);
    expect(container.textContent).toContain("class Client {}");
  });
  it("switches language", () => {
    const code = { typescript: "TS_CODE", python: "PY_CODE" };
    const { container } = render(<SdkCodegenPanel generatedCode={code} languages={["typescript", "python"]} />);
    const pyBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "python")!;
    fireEvent.click(pyBtn);
    expect(container.textContent).toContain("PY_CODE");
  });
});
