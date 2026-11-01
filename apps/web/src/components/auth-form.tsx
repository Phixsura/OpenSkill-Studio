"use client";

import { useState } from "react";

interface Provider { id: string; label: string; icon?: string; }
interface AuthFormProps { mode: "login" | "register"; providers: Provider[];
  onSubmit: (data: { email: string; password: string; name?: string }) => void;
  onProviderAuth: (providerId: string) => void; }

export function AuthForm({ mode, providers, onSubmit, onProviderAuth }: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  return (
    <div className="mx-auto max-w-sm space-y-4">
      <h1 className="text-center text-2xl font-bold">{mode === "login" ? "Sign In" : "Create Account"}</h1>
      {providers.length > 0 && (
        <div className="space-y-2">
          {providers.map(p => (
            <button key={p.id} onClick={() => onProviderAuth(p.id)}
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-200 py-2.5 text-sm hover:bg-gray-50 dark:border-gray-700">
              {p.icon && <span>{p.icon}</span>} {p.label}
            </button>
          ))}
          <div className="flex items-center gap-3 text-xs text-gray-400">
            <hr className="flex-1" /><span>or</span><hr className="flex-1" />
          </div>
        </div>
      )}
      <div className="space-y-3">
        {mode === "register" && (
          <input value={name} onChange={e => setName(e.target.value)} placeholder="Display Name"
            className="w-full rounded-lg border px-4 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
        )}
        <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" type="email"
          className="w-full rounded-lg border px-4 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <input value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" type="password"
          className="w-full rounded-lg border px-4 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
      </div>
      <button onClick={() => onSubmit({ email, password, name: mode === "register" ? name : undefined })}
        disabled={!email || !password}
        className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
        {mode === "login" ? "Sign In" : "Create Account"}
      </button>
    </div>
  );
}
