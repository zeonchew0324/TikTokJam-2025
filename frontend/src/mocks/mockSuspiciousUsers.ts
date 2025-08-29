import type { SuspiciousUser } from '../types/admin'

export const mockSuspiciousUsers: SuspiciousUser[] = [
  {
    userId: 'usr_1a2b3c',
    username: 'user_alpha',
    avatarUrl: 'https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/43564c78f52c612a350543c333019967~c5_720x720.jpeg',
    suspicionScore: 92,
    reason: 'Anomalous API call frequency.',
    detectedAt: '2025-08-29T10:30:00Z'
  },
  {
    userId: 'usr_d4e5f6',
    username: 'repost_king_01',
    avatarUrl: 'https://p16-sign-sg.tiktokcdn.com/aweme/100x100/tiktok-obj/166819179709441.jpg',
    suspicionScore: 88,
    reason: 'Duplicate content hash activity across accounts.',
    detectedAt: '2025-08-29T12:10:00Z'
  },
  {
    userId: 'usr_g7h8i9',
    username: 'loop_view_bot',
    avatarUrl: 'https://p16-sign-va.tiktokcdn.com/musically-maliva-obj/1665841411021829~c5_720x720.jpeg',
    suspicionScore: 95,
    reason: 'Unnatural view loops from same device cluster.',
    detectedAt: '2025-08-29T13:45:00Z'
  }
]


