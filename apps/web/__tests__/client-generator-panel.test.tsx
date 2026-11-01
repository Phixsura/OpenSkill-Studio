import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ClientGeneratorPanel } from "@/components/client-generator-panel";

const mockClient = {
  className: "UserServiceClient", baseUrl: "https://api.example.com",
  authType: "bearer",
  methods: [
    { name: "listUsers", method: "GET", path: "/api/users", hasBody: false, description: "List users" },
    { name: "createUser", method: "POST", path: "/api/users", hasBody: true, description: "Create user" },
  ],
};

describe("ClientGeneratorPanel", () => {
  it("renders client info", () => {
    const { container } = render(
      <ClientGeneratorPanel client={mockClient} generatedCode="" />
    );
    expect(container.textContent).toContain("UserServiceClient");
    expect(container.textContent).toContain("listUsers()");
    expect(container.textContent).toContain("bearer");
  });

  it("shows generated code", () => {
    const { container } = render(
      <ClientGeneratorPanel client={mockClient} generatedCode="class UserServiceClient { }" />
    );
    expect(container.textContent).toContain("class UserServiceClient");
  });

  it("calls onGenerate", () => {
    const onGenerate = vi.fn();
    const { getByText } = render(
      <ClientGeneratorPanel client={null} generatedCode="" onGenerate={onGenerate} />
    );
    fireEvent.click(getByText("Generate"));
    expect(onGenerate).toHaveBeenCalledWith("typescript");
  });

  it("switches language", () => {
    const onGenerate = vi.fn();
    const { getByText } = render(
      <ClientGeneratorPanel client={null} generatedCode="" onGenerate={onGenerate} />
    );
    fireEvent.click(getByText("Python"));
    fireEvent.click(getByText("Generate"));
    expect(onGenerate).toHaveBeenCalledWith("python");
  });
});
