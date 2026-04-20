import { S3Client } from "@aws-sdk/client-s3";

// Cloudflare R2 configuration
export const r2Client = new S3Client({
  region: "auto", // R2 uses "auto" region
  endpoint: process.env.R2_ENDPOINT,
  credentials: {
    accessKeyId: process.env.R2_ACCESS_KEY_ID!,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY!,
  },
});

export const R2_BUCKET_NAME = process.env.R2_BUCKET_NAME!;

// Supported file types for document upload
export const SUPPORTED_FILE_TYPES = {
  'application/pdf': '.pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
} as const;

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes

// Generate a unique file path for R2
export function generateR2FilePath(userId: string, originalFilename: string): string {
  const timestamp = Date.now();
  const randomId = Math.random().toString(36).substring(2, 8);
  const cleanFilename = originalFilename.replace(/[^a-zA-Z0-9.-]/g, '_');

  return `uploads/${userId}/${timestamp}-${randomId}-${cleanFilename}`;
}

// Get public URL for R2 object
export function getR2PublicUrl(filePath: string): string {
  return `${process.env.R2_PUBLIC_URL}/${filePath}`;
}