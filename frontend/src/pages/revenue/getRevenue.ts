// src/services/api.ts

// --- Type Definitions (Unchanged) ---

export type VideoSummary = {
  videoId: string
  thumbnailUrl: string
  title: string
  totalRevenue: number
  views: number
  likes: number
  comments: number
}

export type CategorySegment = {
  categoryId: 'education' | 'cooking' | 'entertainment'
  name: string
  percentContribution: number
  totalRevenue: number
  monthlyRevenue: number
  engagementScore: number
  rankPercent: number
  tier: 'A' | 'B' | 'C' | 'D'
  nextTierRequirement: number | null
}

export type RevenueResponse = {
  videoId: string
  totalEngagementScore: number
  categories: CategorySegment[]
}

// --- API Integration ---

// Get the backend URL from your .env file.
// For Vite, this would be VITE_API_URL. For Next.js, NEXT_PUBLIC_API_URL.
const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetches a summary of all user videos from the backend.
 */
export async function fetchUserVideos(): Promise<VideoSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/videos`);

  if (!response.ok) {
    // In a real app, you'd want more robust error handling here.
    throw new Error(`Failed to fetch videos: ${response.statusText}`);
  }

  const data: VideoSummary[] = await response.json();
  return data;
}

/**
 * Fetches detailed revenue and category data for a specific video.
 * @param videoId The ID of the video to fetch details for.
 */
export async function fetchVideoRevenue(videoId: string): Promise<RevenueResponse> {
  if (!videoId) {
    throw new Error('A video ID must be provided.');
  }

  const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/revenue`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Video with ID "${videoId}" not found.`);
    }
    throw new Error(`Failed to fetch video revenue: ${response.statusText}`);
  }

  const data: RevenueResponse = await response.json();
  return data;
}