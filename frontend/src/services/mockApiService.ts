import { mockSuspiciousUsers } from '../mocks/mockSuspiciousUsers'
import { mockCategories } from '../mocks/mockCategories'
import type { SuspiciousUser, Category } from '../types/admin'

const delay = (ms: number) => new Promise(res => setTimeout(res, ms))

export const mockApiService = {
  runBotScan: async (): Promise<{ status: 'complete' }> => {
    await delay(2500)
    return { status: 'complete' }
  },
  getSuspiciousUsers: async (): Promise<SuspiciousUser[]> => {
    await delay(500)
    return mockSuspiciousUsers
  },
  getVideoCategories: async (): Promise<Category[]> => {
    await delay(300)
    return mockCategories
  }
}


