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

function getVideoTotalRevenue(videoId: string): number {
  // Use fixed values for known IDs (so list and detail stay consistent)
  if (videoId === 'vid-001') return 123.45
  if (videoId === 'vid-002') return 256.7
  if (videoId === 'vid-003') return 98.12
  // Fallback deterministic amount based on id
  const base = Array.from(videoId).reduce((s, c) => s + c.charCodeAt(0), 0)
  return Number((80 + (base % 150) + 0.37).toFixed(2))
}

function splitByPercentages(total: number, percents: number[]): number[] {
  // Round to 2 decimals and adjust last slice to fix rounding drift
  const raw = percents.map(p => (total * p) / 100)
  const rounded = raw.map((v) => Number(v.toFixed(2)))
  const diff = Number((total - rounded.reduce((a, b) => a + b, 0)).toFixed(2))
  // Add the tiny difference to the last item to guarantee exact sum
  rounded[rounded.length - 1] = Number((rounded[rounded.length - 1] + diff).toFixed(2))
  return rounded
}

export async function fetchUserVideosMock(): Promise<VideoSummary[]> {
  await new Promise(r => setTimeout(r, 200))
  return [
    { videoId: 'vid-001', thumbnailUrl: 'https://picsum.photos/seed/vid001/120/120', title: 'My first dance challenge', totalRevenue: getVideoTotalRevenue('vid-001'), views: 182340, likes: 15420, comments: 982 },
    { videoId: 'vid-002', thumbnailUrl: 'https://picsum.photos/seed/vid002/120/120', title: 'Cooking quick ramen hacks', totalRevenue: getVideoTotalRevenue('vid-002'), views: 345210, likes: 28455, comments: 2110 },
    { videoId: 'vid-003', thumbnailUrl: 'https://picsum.photos/seed/vid003/120/120', title: 'Guitar riff tutorial', totalRevenue: getVideoTotalRevenue('vid-003'), views: 92310, likes: 6420, comments: 350 },
  ]
}

export async function fetchVideoRevenueMock(videoId: string): Promise<RevenueResponse> {
  await new Promise(r => setTimeout(r, 200))
  const base = Array.from(videoId).reduce((s, c) => s + c.charCodeAt(0), 0) % 50
  const tierFor = (score: number): 'A' | 'B' | 'C' | 'D' => {
    if (score >= 85) return 'A'
    if (score >= 70) return 'B'
    if (score >= 55) return 'C'
    return 'D'
  }
  const nextReq = (score: number) => {
    if (score >= 85) return null
    const next = score >= 70 ? 85 : score >= 55 ? 70 : 55
    return Math.max(next - score, 0)
  }
  const totalEngagementScore = 120 + base * 2
  const totalRevenue = getVideoTotalRevenue(videoId)
  const percents = [40, 35, 25]
  const [revEducation, revCooking, revEntertainment] = splitByPercentages(totalRevenue, percents)
  return {
    videoId,
    totalEngagementScore,
    categories: [
      (() => { const pct = percents[0]; const engagement = Math.round(totalEngagementScore * (pct / 100)); return { categoryId: 'education', name: 'Educational', percentContribution: pct, totalRevenue: revEducation, monthlyRevenue: Number((revEducation * 0.25).toFixed(2)), engagementScore: engagement, rankPercent: Math.max(5, 40 - (base % 10)), tier: tierFor(engagement), nextTierRequirement: nextReq(engagement) } })(),
      (() => { const pct = percents[1]; const engagement = Math.round(totalEngagementScore * (pct / 100)); return { categoryId: 'cooking', name: 'Cooking', percentContribution: pct, totalRevenue: revCooking, monthlyRevenue: Number((revCooking * 0.25).toFixed(2)), engagementScore: engagement, rankPercent: Math.max(3, 25 - (base % 8)), tier: tierFor(engagement), nextTierRequirement: nextReq(engagement) } })(),
      (() => { const pct = percents[2]; const engagement = Math.round(totalEngagementScore * (pct / 100)); return { categoryId: 'entertainment', name: 'Entertainment', percentContribution: pct, totalRevenue: revEntertainment, monthlyRevenue: Number((revEntertainment * 0.25).toFixed(2)), engagementScore: engagement, rankPercent: Math.max(1, 12 - (base % 6)), tier: tierFor(engagement), nextTierRequirement: nextReq(engagement) } })(),
    ],
  }
}


