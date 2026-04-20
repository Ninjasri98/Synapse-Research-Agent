"use client";

import { useState, useEffect, useCallback, memo, useRef } from "react";
import {
  Loader2,
  Send,
} from "lucide-react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MarkdownComponents } from "@/components/ui/markdown-components";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

// Chat message type
type Message = {
  role: "user" | "assistant";
  content: string;
};

// API response type
type ChatApiResponse = {
  status: "success" | "error";
  response: string;
};

// Memoized message component to prevent re-renders
const ChatMessage = memo(({ message }: { message: Message }) => (
  <div
    className={`flex ${
      message.role === "user" ? "justify-end" : "justify-start"
    }`}
  >
    <div
      className={`max-w-[80%] px-4 py-2 rounded-lg ${
        message.role === "user"
          ? "bg-primary text-primary-foreground"
          : "bg-muted"
      }`}
    >
      {message.role === "assistant" ? (
        <div className="markdown-container prose prose-sm max-w-none dark:prose-invert">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={MarkdownComponents}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      ) : (
        message.content
      )}
    </div>
  </div>
));

ChatMessage.displayName = "ChatMessage";

// Memoized ChatInterface component to prevent unnecessary re-renders
const ChatInterface = memo(
  ({
    messages,
    isLoading,
    onSendMessage,
  }: {
    messages: Message[];
    isLoading: boolean;
    onSendMessage: (message: string) => void;
  }) => {
    // Local state for input to avoid parent component re-renders when typing
    const [localInput, setLocalInput] = useState("");

    // Use callback ref for textarea to ensure focus
    const textareaRef = useCallback((textareaElement: HTMLTextAreaElement) => {
      if (textareaElement) {
        // Focus the textarea on mount
        textareaElement.focus();
      }
    }, []);

    // Ref for the messages container to control scrolling
    const messagesContainerRef = useRef<HTMLDivElement>(null);

    // Scroll to bottom when messages change
    useEffect(() => {
      if (messagesContainerRef.current) {
        messagesContainerRef.current.scrollTop =
          messagesContainerRef.current.scrollHeight;
      }
    }, [messages, isLoading]);

    const handleSubmit = () => {
      if (!localInput.trim()) return;
      onSendMessage(localInput);
      setLocalInput("");
    };

    return (
      <div className="w-full">
        <div
          ref={messagesContainerRef}
          className="flex flex-col space-y-4 mb-4 h-[400px] overflow-y-auto p-4 border rounded-md"
        >
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              Start a conversation with your notebook
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] px-4 py-2 rounded-lg bg-muted flex items-center">
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Thinking...
              </div>
            </div>
          )}
        </div>

        <div className="flex space-x-2">
          <Textarea
            ref={textareaRef}
            rows={1}
            value={localInput}
            onChange={(e) => setLocalInput(e.target.value)}
            placeholder={`Decipher anything about this notebook...`}
            className="resize-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
          />
          <Button
            onClick={handleSubmit}
            disabled={isLoading || !localInput.trim()}
            className="px-4"
            data-umami-event="frontend_chat_message_send"
            data-umami-event-notebook-id={window.location.pathname
              .split("/")
              .pop()}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    );
  }
);

ChatInterface.displayName = "ChatInterface";
