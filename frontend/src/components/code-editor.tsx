"use client"

import type React from "react"
import { useRef, useEffect } from "react"
import Editor from "react-simple-code-editor"
import { highlight } from "../lib/dslHighlight"
import "prismjs/themes/prism-coy.css"

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
}

export default function CodeEditor({ value, onChange }: CodeEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Tab") {
      e.preventDefault()
      const target = e.target as HTMLTextAreaElement
      const start = target.selectionStart
      const end = target.selectionEnd
      const newValue = value.substring(0, start) + "  " + value.substring(end)
      onChange(newValue)
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 2
        }
      }, 0)
    }
  }

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [value])

  return (
    <Editor
      value={value}
      onValueChange={onChange}
      highlight={highlight}
      padding={16}
      textareaId="codeArea"
      textareaClassName="font-mono"
      className="rounded-lg border bg-zinc-900 text-white shadow-lg min-h-[400px] focus:outline-none"
      style={{
        fontFamily: 'Fira Mono, Menlo, Monaco, "Consolas", monospace',
        fontSize: 16,
        background: "#f8fafc",
        color: "#222",
      }}
      onKeyDown={handleKeyDown}
    />
  )
}
