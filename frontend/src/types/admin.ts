export type SuspiciousUser = {
  userId: string
  username: string
  avatarUrl: string
  suspicionScore: number
  reason: string
  detectedAt: string
}

export type SpamNetwork = {
  networkId: string
  primaryUser: { userId: string; username: string }
  associatedAccountCount: number
  detectionReason: string
  firstDetected: string
}

export type Category = {
  categoryId: string
  name: string
  popularityPercentage: number
}


