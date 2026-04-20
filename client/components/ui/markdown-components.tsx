import type { Components } from "react-markdown";
import Image from "next/image";

// Markdown styling components for ReactMarkdown
export const MarkdownComponents: Components = {
  h1: (props) => (
    <h1 className="text-2xl font-bold mb-4 text-primary mt-6" {...props} />
  ),
  h2: (props) => (
    <h2 className="text-xl font-bold mb-3 text-primary mt-5" {...props} />
  ),
  h3: (props) => <h3 className="text-lg font-bold mb-2 mt-4" {...props} />,
  ul: (props) => <ul className="list-disc pl-5 mb-4 space-y-1" {...props} />,
  ol: (props) => <ol className="list-decimal pl-5 mb-4 space-y-1" {...props} />,
  li: (props) => <li className="mb-1" {...props} />,
  p: (props) => <p className="mb-4" {...props} />,
  strong: (props) => <strong className="font-bold" {...props} />,
  em: (props) => <em className="italic" {...props} />,
  a: (props) => (
    <a
      className="text-blue-600 hover:underline"
      target="_blank"
      rel="noopener noreferrer"
      {...props}
    />
  ),
  table: (props) => (
    <div className="overflow-x-auto mb-6">
      <table
        className="min-w-full divide-y divide-gray-300 border"
        {...props}
      />
    </div>
  ),
  thead: (props) => (
    <thead className="bg-gray-100 dark:bg-gray-800" {...props} />
  ),
  tbody: (props) => (
    <tbody
      className="divide-y divide-gray-200 dark:divide-gray-700"
      {...props}
    />
  ),
  tr: (props) => (
    <tr className="hover:bg-gray-50 dark:hover:bg-gray-900" {...props} />
  ),
  th: (props) => (
    <th
      className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100"
      {...props}
    />
  ),
  td: (props) => <td className="px-4 py-3 text-sm" {...props} />,
  blockquote: (props) => (
    <blockquote
      className="border-l-4 border-gray-300 dark:border-gray-700 pl-4 italic text-gray-700 dark:text-gray-300 my-4"
      {...props}
    />
  ),
  code: (props) => {
    return (
      <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md overflow-x-auto mb-4">
        <code className="text-sm" {...props} />
      </pre>
    );
  },
  hr: (props) => (
    <hr
      className="my-6 border-t border-gray-300 dark:border-gray-700"
      {...props}
    />
  ),
  img: ({ src, alt }) => {
    if (!src) return null;

    // Use default image if src is not a valid URL
    let imageSrc = "";
    try {
      imageSrc = src.toString();
      // Simple URL validation
      new URL(imageSrc);
    } catch {
      // If URL is invalid, use a placeholder Image instead of <img>
      return (
        <div className="my-4 relative">
          <Image
            src="/placeholder-image.jpg" // Placeholder image
            alt={alt || ""}
            width={700}
            height={350}
            className="max-w-full h-auto rounded"
            style={{ objectFit: "contain" }}
            unoptimized
          />
        </div>
      );
    }

    return (
      <div className="my-4 relative">
        <Image
          src={imageSrc}
          alt={alt || ""}
          width={700}
          height={350}
          className="max-w-full h-auto rounded"
          style={{ objectFit: "contain" }}
          unoptimized
        />
      </div>
    );
  },
};
