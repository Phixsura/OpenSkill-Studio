"use client";

import { useState } from "react";

interface Channel { id: string; label: string; icon: string; description: string; url: string; }
interface ContactPageLayoutProps { channels: Channel[]; onSubmit: (data: { name: string; email: string; subject: string; message: string }) => void; }

export function ContactPageLayout({ channels, onSubmit }: ContactPageLayoutProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("General");
  const [message, setMessage] = useState("");

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Get in Touch</h1>
        <p className="mt-2 text-sm text-gray-500">We would love to hear from you</p>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {channels.map(c => (
          <a key={c.id} href={c.url} className="rounded-lg border border-gray-200 p-4 text-center transition hover:shadow-md dark:border-gray-700">
            <span className="text-2xl">{c.icon}</span>
            <h3 className="mt-2 text-sm font-semibold">{c.label}</h3>
            <p className="mt-1 text-xs text-gray-400">{c.description}</p>
          </a>
        ))}
      </div>
      <div className="rounded-lg border border-gray-200 p-6 dark:border-gray-700">
        <h2 className="text-lg font-semibold">Send a Message</h2>
        <div className="mt-4 grid grid-cols-2 gap-4">
          <input value={name} onChange={e => setName(e.target.value)} placeholder="Name"
            className="rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
          <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" type="email"
            className="rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
        <select value={subject} onChange={e => setSubject(e.target.value)}
          className="mt-3 w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700">
          {["General", "Bug Report", "Feature Request", "Billing"].map(s => <option key={s}>{s}</option>)}
        </select>
        <textarea value={message} onChange={e => setMessage(e.target.value)} rows={4} placeholder="Your message..."
          className="mt-3 w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <button onClick={() => onSubmit({ name, email, subject, message })}
          disabled={!name || !email || !message}
          className="mt-4 w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
          Send Message
        </button>
      </div>
    </div>
  );
}
